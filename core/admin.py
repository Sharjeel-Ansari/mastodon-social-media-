from django.contrib import admin
from .models import User, Post, Comment, Like, Follow, Notification

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'followers_count', 'following_count', 'posts_count')

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('author', 'content', 'likes_count', 'comments_count', 'created_at')

admin.site.register(Comment)
admin.site.register(Like)
admin.site.register(Follow)
admin.site.register(Notification)
