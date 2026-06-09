from django.urls import path
from . import views

urlpatterns = [
    # Auth
    path('auth/register/', views.register_view, name='register'),
    path('auth/login/', views.login_view, name='login'),
    path('auth/logout/', views.logout_view, name='logout'),

    # Feed
    path('', views.feed_view, name='feed'),
    path('explore/', views.explore_view, name='explore'),

    # Posts
    path('posts/create/', views.create_post, name='create_post'),
    path('posts/<int:post_id>/', views.post_detail, name='post_detail'),
    path('posts/<int:post_id>/delete/', views.delete_post, name='delete_post'),

    # Likes & Comments
    path('posts/<int:post_id>/like/', views.toggle_like, name='toggle_like'),
    path('posts/<int:post_id>/comment/', views.add_comment, name='add_comment'),
    path('comments/<int:comment_id>/delete/', views.delete_comment, name='delete_comment'),

    # Follow
    path('users/<str:username>/follow/', views.toggle_follow, name='toggle_follow'),

    # Profile
    path('profile/<str:username>/', views.profile_view, name='profile'),
    path('profile/edit/me/', views.edit_profile, name='edit_profile'),

    # Notifications
    path('notifications/', views.notifications_view, name='notifications'),
]
