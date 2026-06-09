from django import template
from core.models import Like, Follow

register = template.Library()

@register.filter
def is_liked(post, user):
    return post.is_liked_by(user)

@register.filter
def is_following(current_user, target_user):
    return Follow.objects.filter(follower=current_user, following=target_user).exists()
