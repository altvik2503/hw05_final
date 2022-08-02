from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.views.decorators.cache import cache_page
from django.contrib.auth.decorators import login_required
from .models import Follow, Group, Post, User
from .forms import PostForm, CommentForm

NUMBER_DISPLAYED_POSTS = 10


def paginator_get_page(posts_list, request):
    paginator = Paginator(posts_list, NUMBER_DISPLAYED_POSTS)
    return paginator.get_page(request.GET.get('page'))


@cache_page(20, key_prefix='index_page')
def index(request):
    posts_list = Post.objects.select_related('group', 'author')
    page_obj = paginator_get_page(posts_list, request)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts_list = group.posts.select_related('group', 'author')
    page_obj = paginator_get_page(posts_list, request)
    context = {
        'page_obj': page_obj,
        'group': group,
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    posts_list = author.posts.select_related('group', 'author')
    page_obj = paginator_get_page(posts_list, request)
    following = None
    if request.user.is_authenticated:
        following = author.following.filter(user=request.user).exists()
    myself = (author == request.user)
    context = {
        'page_obj': page_obj,
        'author': author,
        'following': following,
        'myself': myself,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm()
    comments = post.comments.select_related('post', 'author')
    context = {
        'post': post,
        'title': post.text[:30],
        'form': form,
        'comments': comments,
    }
    return render(request, 'posts/post_detail.html', context)


def post_create(request):
    if request.user.is_authenticated:
        form = PostForm(request.POST or None)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('posts:profile', post.author.username)
        context = {
            'form': form,
            'title': 'Новый пост',
        }
        return render(request, 'posts/create_post.html', context)
    return redirect('posts:index')


def post_edit(request, post_id):
    post = Post.objects.select_related('author').get(id=post_id)
    if request.user != post.author:
        return redirect('posts:post_detail', post_id=post_id)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )

    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id)
    context = {
        'form': form,
        'is_edit': True,
        'title': 'Редактировать пост',
    }
    return render(request, 'posts/create_post.html', context)


@login_required
def add_comment(request, post_id):
    if request.user.is_authenticated:
        post = get_object_or_404(Post, id=post_id)
        form = CommentForm(request.POST or None)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.author = request.user
            comment.post = post
            comment.save()
    return redirect('posts:post_detail', post_id)


@login_required
def follow_index(request):
    user = request.user
    follows_list = Follow.objects.filter(user=user)
    authors_list = set()
    for follow in follows_list:
        authors_list.add(follow.author)
    posts_list = Post.objects.filter(
        author__in=authors_list
    ).select_related('group', 'author')
    page_obj = paginator_get_page(posts_list, request)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if author != request.user:
        Follow.objects.get_or_create(
            author=author,
            user=request.user
        )
    return redirect('posts:profile', username)


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    author.following.filter(user=request.user).delete()
    return redirect('posts:profile', username)
