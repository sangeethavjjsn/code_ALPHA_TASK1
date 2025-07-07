from django.contrib import admin
from .models import User, Post, Comment, Follow
from .models import Message  # 👈 add this if not already there
admin.site.register(Message)  # 👈 this line registers the Message model
admin.site.register(User)
admin.site.register(Post)
admin.site.register(Comment)
admin.site.register(Follow)
from django.contrib import admin
from .models import UserProfile, FollowRequest

admin.site.register(UserProfile)
admin.site.register(FollowRequest)