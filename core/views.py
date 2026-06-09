from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db.models import Q
from django.contrib import messages
from .models import User, Post, Comment, Like, Follow, Notification
from .forms import RegisterForm, LoginForm, PostForm, ProfileEditForm, CommentForm


# ─── Auth Views ───────────────────────────────────────────────────────────────

def register_view(request):
    if request.user.is_authenticated:
        return redirect('feed')
    form = RegisterForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, f'Welcome to Vibe, {user.username}! 🎉')
        return redirect('feed')
    return render(request, 'auth/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('feed')
    form = LoginForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            next_url = request.GET.get('next', 'feed')
            return redirect(next_url)
        else:
            form.add_error(None, 'Invalid username or password.')
    return render(request, 'auth/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('login')


# ─── Feed ─────────────────────────────────────────────────────────────────────

@login_required
def feed_view(request):
    # Show posts from followed users + own posts
    following_users = request.user.following.values_list('following', flat=True)
    posts = Post.objects.filter(
        Q(author__in=following_users) | Q(author=request.user)
    ).select_related('author').prefetch_related('likes', 'comments')

    post_form = PostForm()
    suggested_users = User.objects.exclude(
        id__in=list(following_users) + [request.user.id]
    ).order_by('?')[:5]

    return render(request, 'feed/index.html', {
        'posts': posts,
        'post_form': post_form,
        'suggested_users': suggested_users,
    })


@login_required
def explore_view(request):
    q = request.GET.get('q', '')
    posts = Post.objects.all().select_related('author').prefetch_related('likes', 'comments')
    users = []
    if q:
        posts = posts.filter(
            Q(content__icontains=q) | Q(author__username__icontains=q)
        )
        users = User.objects.filter(
            Q(username__icontains=q) | Q(first_name__icontains=q) | Q(last_name__icontains=q)
        ).exclude(id=request.user.id)[:10]
    following_users = request.user.following.values_list('following', flat=True)
    suggested_users = User.objects.exclude(
        id__in=list(following_users) + [request.user.id]
    ).order_by('?')[:5]
    return render(request, 'feed/explore.html', {
        'posts': posts,
        'users': users,
        'query': q,
        'suggested_users': suggested_users,
    })


# ─── Posts ────────────────────────────────────────────────────────────────────

@login_required
@require_POST
def create_post(request):
    form = PostForm(request.POST, request.FILES)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'post_id': post.id,
                'author': post.author.username,
                'content': post.content,
                'created_at': post.created_at.strftime('%b %d, %Y'),
                'avatar': post.author.get_avatar_url(),
            })
    return redirect('feed')


@login_required
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id, author=request.user)
    post.delete()
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True})
    return redirect('feed')


@login_required
def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    comments = post.comments.select_related('author').all()
    comment_form = CommentForm()
    return render(request, 'feed/post_detail.html', {
        'post': post,
        'comments': comments,
        'comment_form': comment_form,
    })


# ─── Likes ────────────────────────────────────────────────────────────────────

@login_required
@require_POST
def toggle_like(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    like, created = Like.objects.get_or_create(post=post, user=request.user)
    if not created:
        like.delete()
        liked = False
    else:
        liked = True
        if post.author != request.user:
            Notification.objects.create(
                recipient=post.author,
                sender=request.user,
                notif_type='like',
                post=post
            )
    return JsonResponse({'liked': liked, 'count': post.likes_count})


# ─── Comments ─────────────────────────────────────────────────────────────────

@login_required
@require_POST
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.post = post
        comment.author = request.user
        comment.save()
        if post.author != request.user:
            Notification.objects.create(
                recipient=post.author,
                sender=request.user,
                notif_type='comment',
                post=post
            )
        return JsonResponse({
            'success': True,
            'comment_id': comment.id,
            'author': comment.author.username,
            'content': comment.content,
            'avatar': comment.author.get_avatar_url(),
            'created_at': comment.created_at.strftime('%b %d'),
            'count': post.comments_count,
        })
    return JsonResponse({'success': False}, status=400)


@login_required
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id, author=request.user)
    post_id = comment.post.id
    comment.delete()
    return JsonResponse({'success': True, 'count': comment.post.comments_count if False else Post.objects.get(id=post_id).comments_count})


# ─── Follow ───────────────────────────────────────────────────────────────────

@login_required
@require_POST
def toggle_follow(request, username):
    target = get_object_or_404(User, username=username)
    if target == request.user:
        return JsonResponse({'error': 'Cannot follow yourself'}, status=400)
    follow, created = Follow.objects.get_or_create(follower=request.user, following=target)
    if not created:
        follow.delete()
        following = False
    else:
        following = True
        Notification.objects.create(
            recipient=target,
            sender=request.user,
            notif_type='follow'
        )
    return JsonResponse({'following': following, 'count': target.followers_count})


# ─── Profile ──────────────────────────────────────────────────────────────────

@login_required
def profile_view(request, username):
    profile_user = get_object_or_404(User, username=username)
    posts = profile_user.posts.prefetch_related('likes', 'comments').all()
    is_following = Follow.objects.filter(follower=request.user, following=profile_user).exists()
    followers = profile_user.followers.select_related('follower').all()
    following = profile_user.following.select_related('following').all()
    return render(request, 'profile/profile.html', {
        'profile_user': profile_user,
        'posts': posts,
        'is_following': is_following,
        'followers': followers,
        'following_list': following,
    })


@login_required
def edit_profile(request):
    form = ProfileEditForm(request.POST or None, request.FILES or None, instance=request.user)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Profile updated!')
        return redirect('profile', username=request.user.username)
    return render(request, 'profile/edit_profile.html', {'form': form})


# ─── Notifications ────────────────────────────────────────────────────────────

@login_required
def notifications_view(request):
    notifs = request.user.notifications.select_related('sender', 'post').all()
    notifs.update(is_read=True)
    return render(request, 'feed/notifications.html', {'notifications': notifs})
