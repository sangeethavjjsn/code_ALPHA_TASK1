from django.urls import path
from . import views

urlpatterns = [
      # dashboard is homepage after login
    path('', views.welcome_page, name='welcome'),
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    # Other routes as-is
    path('create_post/', views.create_post, name='create_post'),
    path('profile/<int:user_id>/', views.profile_view, name='profile_view'),
    path('edit_profile/', views.edit_profile, name='edit_profile'),
    path('post/delete/<int:post_id>/', views.delete_post, name='delete_post'),
    path('follow/<int:user_id>/', views.follow_user, name='follow_user'),
    path('unfollow/<int:user_id>/', views.unfollow_user, name='unfollow_user'),
    path('inbox/', views.inbox, name='inbox'),
    path('chat/<int:user_id>/', views.chat, name='chat'),
    path('chat/<int:user_id>/fetch/', views.fetch_messages, name='fetch_messages'),
    path('send_message/<int:user_id>/', views.send_message, name='send_message'),
    path('fetch_messages/<int:user_id>/', views.fetch_messages, name='fetch_messages'),
    path('search/', views.search_users, name='search_users'),
    path('search_page/', views.search_page, name='search_page'),
    path('followers/<int:user_id>/', views.followers_list, name='followers_list'),
    path('following/<int:user_id>/', views.following_list, name='following_list'),
    path('follow/<int:user_id>/', views.send_follow_request, name='send_follow_request'),
    path('follow/<int:user_id>/', views.follow_user, name='follow_user'),
    path('unfollow/<int:user_id>/', views.unfollow_user, name='unfollow_user'),
    path('followers-count/<int:user_id>/', views.followers_count, name='followers_count'),

    path('request/<int:request_id>/<str:action>/', views.respond_to_request, name='respond_to_request'),
    path('cancel_request/<int:request_id>/', views.cancel_request, name='cancel_request'),
    path('post/<int:post_id>/', views.post_detail, name='post_detail'),
    path('like_post/<int:post_id>/', views.like_post, name='like_post'),
    path('delete_post/<int:post_id>/', views.delete_post, name='delete_post'),
    path('add_comment/<int:post_id>/', views.add_comment, name='add_comment'),
    path('delete_comment/<int:comment_id>/', views.delete_comment, name='delete_comment'),
    path('save_post/<int:post_id>/', views.save_post, name='save_post'),
    path('delete_for_me/<int:message_id>/', views.delete_message_for_me, name='delete_for_me'),
    path('delete_for_everyone/<int:message_id>/', views.delete_message_for_everyone, name='delete_for_everyone'),
    path('delete_bulk/', views.delete_bulk, name='delete_bulk'),

]
