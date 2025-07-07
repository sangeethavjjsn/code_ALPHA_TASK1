from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate, logout
from django.db.models import Q
from .forms import RegisterForm, LoginForm, PostForm, CommentForm, ProfileEditForm
from .models import User, Post, Comment, Follow, Message, Profile
from django.contrib import messages
from django.http import JsonResponse,HttpResponseForbidden
from django.core import serializers
from django.views.decorators.csrf import csrf_exempt
from .models import FollowRequest, UserProfile
import json


def welcome_page(request):
    return render(request, 'welcome.html')

# Signup view
def signup_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Account created for {}'.format(user.username))
            return redirect('login')
    else:
        form = RegisterForm()
    return render(request, 'signup.html', {'form': form})

# Login view
def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return redirect('dashboard')
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})

# Dashboard
@login_required
def dashboard(request):
    posts = Post.objects.prefetch_related('comments', 'likes', 'saves').order_by('-created_at')
    liked_posts = Post.objects.filter(likes=request.user)
    return render(request, 'dashboard.html', {
        'posts': posts,
        'liked_posts': liked_posts
    })

# Create Post
@login_required
def create_post(request):
    if request.method == 'POST':
        caption = request.POST.get('caption')
        image = request.FILES.get('image')
        if caption and image:
            Post.objects.create(author=request.user, caption=caption, image=image)
            return redirect('dashboard')
        else:
            return render(request, 'create_post.html', {'error': 'Both fields required.'})
    return render(request, 'create_post.html')
@csrf_exempt
@login_required
def delete_post(request, post_id):
    try:
        post = Post.objects.get(id=post_id)
        if request.user == post.author:
            post.delete()
            return JsonResponse({'success': True})
        return JsonResponse({'success': False, 'error': 'Unauthorized'}, status=403)
    except Post.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Post not found'}, status=404)
# Logout
def logout_view(request):
    logout(request)
    return redirect('login')

# Profile View
@login_required
def profile_view(request, user_id):
    profile = get_object_or_404(Profile, user__id=user_id)
    posts = Post.objects.filter(author=profile.user)
    followers_count = Follow.objects.filter(following=profile.user).count()
    following_count = Follow.objects.filter(follower=profile.user).count()

    return render(request, 'profile.html', {
        'profile': profile,
        'posts': posts,
        'followers_count': followers_count,
        'following_count': following_count
    })

# Edit Profile
@login_required
def edit_profile(request):
    profile = get_object_or_404(Profile, user=request.user)

    if request.method == 'POST':
        bio = request.POST.get('bio')
        image = request.FILES.get('profile_pic')

        if bio:
            profile.bio = bio
        if image:
            profile.profile_pic = image

        profile.save()
        return redirect('profile_view', user_id=request.user.id)

    return render(request, 'edit_profile.html', {
        'profile': profile,
        'user_id': request.user.id
    })

# Delete Post
@login_required
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if post.author == request.user:
        post.delete()
        messages.success(request, "Your post has been deleted successfully.")
    else:
        messages.error(request, "You are not authorized to delete this post.")
    return redirect('dashboard')

# Follow / Unfollow
@login_required
def follow_user(request, user_id):
    user_to_follow = get_object_or_404(User, id=user_id)
    if user_to_follow != request.user:
        Follow.objects.get_or_create(follower=request.user, following=user_to_follow)
    return redirect('profile_view', user_id=user_id)

@login_required
def unfollow_user(request, user_id):
    user_to_unfollow = get_object_or_404(User, id=user_id)
    Follow.objects.filter(follower=request.user, following=user_to_unfollow).delete()
    return redirect('profile_view', user_id=user_id)

# Inbox & Chat
@login_required
def inbox(request):
    # Get all distinct users involved in chats with current user
    user_ids = Message.objects.filter(
        Q(sender=request.user) | Q(receiver=request.user)
    ).values_list('sender_id', 'receiver_id')

    # Flatten IDs and remove current user ID
    unique_user_ids = set()
    for sender_id, receiver_id in user_ids:
        if sender_id != request.user.id:
            unique_user_ids.add(sender_id)
        if receiver_id != request.user.id:
            unique_user_ids.add(receiver_id)

    # Fetch those user profiles
    users = User.objects.filter(id__in=unique_user_ids).select_related('profile')

    # Prepare latest message and time for each conversation
    messages_data = []
    for user in users:
        latest_msg = Message.objects.filter(
            Q(sender=request.user, receiver=user) | Q(sender=user, receiver=request.user)
        ).order_by('-timestamp').first()

        messages_data.append({
            'user': user,
            'latest_msg': latest_msg.text if latest_msg else "No messages yet",
            'time': latest_msg.timestamp.strftime("%I:%M %p") if latest_msg else ""
        })

    return render(request, 'inbox.html', {'messages_data': messages_data})

from django.http import JsonResponse

@login_required
def chat(request, user_id):
    other_user = get_object_or_404(User, id=user_id)

    # Handle AJAX message sending
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        text = request.POST.get('text')
        if text:
            Message.objects.create(sender=request.user, receiver=other_user, text=text)
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False})

    # Load messages
    messages_qs = Message.objects.filter(
        Q(sender=request.user, receiver=other_user) |
        Q(sender=other_user, receiver=request.user)
    ).filter(deleted_globally=False).exclude(
        Q(sender=request.user, deleted_for_sender=True) |
        Q(receiver=request.user, deleted_for_receiver=True)
    ).order_by('timestamp')

    return render(request, 'chat.html', {
        'other_user': other_user,
        'messages': messages_qs
    })


# Search Users
@login_required
def search_users(request):
    query = request.GET.get('q')
    users = User.objects.filter(username__icontains=query).exclude(id=request.user.id) if query else []
    return render(request, 'search_results.html', {'users': users, 'query': query})

@login_required
def search_page(request):
    return render(request, 'search_page.html')

# Followers / Following Lists
@login_required
def followers_list(request, user_id):
    user = get_object_or_404(User, id=user_id)
    followers = Follow.objects.filter(following=user)
    return render(request, 'followers_list.html', {'user': user, 'followers': followers})

@login_required
def following_list(request, user_id):
    user = get_object_or_404(User, id=user_id)
    following = Follow.objects.filter(follower=user)
    return render(request, 'following_list.html', {'user': user, 'following': following})

def like_post(request, post_id):
    if request.method == 'POST':
        post = get_object_or_404(Post, id=post_id)
        if request.user in post.likes.all():
            post.likes.remove(request.user)
            liked = False
        else:
            post.likes.add(request.user)
            liked = True
        return JsonResponse({'liked': liked, 'likes_count': post.likes.count()})
    else:
        return HttpResponseForbidden()

# Post Detail
@login_required
def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    return render(request, 'post_detail.html', {'post': post})

# Delete for me
@login_required
def delete_message_for_me(request, message_id):
    message = get_object_or_404(Message, id=message_id)

    if message.sender == request.user:
        message.deleted_for_sender = True
    elif message.receiver == request.user:
        message.deleted_for_receiver = True

    message.save()
    return redirect('chat', user_id=message.receiver.id if request.user == message.sender else message.sender.id)

# Delete for everyone
@login_required
def delete_message_for_everyone(request, message_id):
    message = get_object_or_404(Message, id=message_id)

    if request.user == message.sender:
        message.deleted_globally = True
        message.save()

    return redirect('chat', user_id=message.receiver.id)



@csrf_exempt
@login_required
def delete_bulk(request):
    if request.method == 'POST':
        ids = request.POST.getlist('selected_msgs')
        action = request.POST.get('action')

        if not ids:
            return JsonResponse({'success': False, 'message': 'No messages selected.'})

        deleted_ids = []
        for msg_id in ids:
            try:
                msg = Message.objects.get(id=msg_id)

                if action == 'delete_for_everyone':
                    # Only sender can delete for everyone
                    if msg.sender == request.user:
                        msg.deleted_globally = True
                        msg.save()
                        deleted_ids.append(msg_id)

                elif action == 'delete_for_me':
                    if request.user == msg.sender:
                        msg.deleted_for_sender = True
                        msg.save()
                        deleted_ids.append(msg_id)
                    elif request.user == msg.receiver:
                        msg.deleted_for_receiver = True
                        msg.save()
                        deleted_ids.append(msg_id)

            except Message.DoesNotExist:
                continue

        return JsonResponse({'success': True, 'deleted_ids': deleted_ids})

    return JsonResponse({'success': False, 'message': 'Invalid request.'})

@login_required
def fetch_messages(request, user_id):
    last_id = int(request.GET.get('last_id', 0))
    other_user = get_object_or_404(User, id=user_id)

    new_msgs = Message.objects.filter(
        Q(sender=request.user, receiver=other_user) |
        Q(sender=other_user, receiver=request.user),
        id__gt=last_id
    ).filter(deleted_globally=False).exclude(
        Q(sender=request.user, deleted_for_sender=True) |
        Q(receiver=request.user, deleted_for_receiver=True)
    ).order_by('timestamp')

    msgs_data = []
    for m in new_msgs:
        msgs_data.append({
            'id': m.id,
            'text': m.text,
            'timestamp': m.timestamp.strftime('%I:%M %p'),
            'is_sender': m.sender == request.user
        })

    return JsonResponse({'messages': msgs_data})

@login_required
def send_message(request, user_id):
    if request.method == 'POST':
        text = request.POST.get('text', '').strip()
        if text:
            Message.objects.create(
                sender=request.user,
                recipient_id=user_id,
                text=text
            )
            return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=400)
# views.py


@login_required
def add_comment(request, post_id):
    if request.method == 'POST':
        text = request.POST.get('text')
        if text:
            post = Post.objects.get(id=post_id)
            comment = Comment.objects.create(
                user=request.user,
                post=post,
                text=text
            )
            return JsonResponse({'success': True, 'comment_id': comment.id})
    return JsonResponse({'success': False})
@login_required
def delete_comment(request, comment_id):
    if request.method == 'POST':
        comment = Comment.objects.get(id=comment_id)
        if comment.user == request.user:
            comment.delete()
            return JsonResponse({'success': True})
    return JsonResponse({'success': False})

@csrf_exempt
@login_required
def save_post(request, post_id):
    if request.method == 'POST':
        post = Post.objects.get(id=post_id)
        if request.user in post.saves.all():
            post.saves.remove(request.user)
            return JsonResponse({'saved': False})
        else:
            post.saves.add(request.user)
            return JsonResponse({'saved': True})
    return JsonResponse({'saved': False})


@login_required
def send_follow_request(request, user_id):
    to_user = get_object_or_404(User, id=user_id)
    
    if request.user == to_user:
        return JsonResponse({'success': False, 'error': "You can't follow yourself"})
    
    profile = to_user.userprofile
    
    if not profile.is_private:
        # Auto-follow if account is public
        request.user.userprofile.following.add(to_user)
        return JsonResponse({'success': True, 'auto_followed': True})
    
    # For private accounts
    if FollowRequest.objects.filter(from_user=request.user, to_user=to_user).exists():
        return JsonResponse({'success': False, 'error': 'Request already sent'})
    
    FollowRequest.objects.create(from_user=request.user, to_user=to_user)
    return JsonResponse({'success': True})

@login_required
def respond_to_request(request, request_id, action):
    follow_request = get_object_or_404(FollowRequest, id=request_id, to_user=request.user)
    
    if action == 'accept':
        request.user.userprofile.followers.add(follow_request.from_user)
        follow_request.is_accepted = True
        follow_request.save()
        return JsonResponse({'success': True})
    elif action == 'decline':
        follow_request.delete()
        return JsonResponse({'success': True})
    
    return JsonResponse({'success': False, 'error': 'Invalid action'})

@login_required
def cancel_request(request, request_id):
    follow_request = get_object_or_404(FollowRequest, id=request_id, from_user=request.user)
    follow_request.delete()
    return JsonResponse({'success': True})
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required

@login_required
def follow_user(request, user_id):
    user_to_follow = get_object_or_404(User, id=user_id)
    if user_to_follow != request.user:
        Follow.objects.get_or_create(follower=request.user, following=user_to_follow)
        follower_count = Follow.objects.filter(following=user_to_follow).count()
        return JsonResponse({'success': True, 'follower_count': follower_count})
    return JsonResponse({'success': False})


@login_required
def unfollow_user(request, user_id):
    user_to_unfollow = get_object_or_404(User, id=user_id)
    Follow.objects.filter(follower=request.user, following=user_to_unfollow).delete()
    follower_count = Follow.objects.filter(following=user_to_unfollow).count()
    return JsonResponse({'success': True, 'follower_count': follower_count})

@login_required
def followers_count(request, user_id):
    user = get_object_or_404(User, id=user_id)
    follower_count = Follow.objects.filter(following=user).count()
    return JsonResponse({'follower_count': follower_count})

