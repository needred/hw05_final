from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from .forms import PostForm, CommentForm
from .models import Follow, Group, Post, User


def index(request):
    """
    Вывод списка постов на главной странице.
    """
    posts = Post.objects.select_related('author', 'group').all()
    paginator = Paginator(posts, settings.PAGINATOR_OBJECTS_PER_PAGE)

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {'page_obj': page_obj}
    template = 'posts/index.html'
    return render(request, template, context)


def group_posts(request, slug):
    """
    Вывод списка постов на странице сообщества.
    """
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.prefetch_related('author').all()
    paginator = Paginator(posts, settings.PAGINATOR_OBJECTS_PER_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'group': group,
        'page_obj': page_obj,
    }
    template = 'posts/group_list.html'
    return render(request, template, context)


def groups(request):
    """
    Отображение списка групп-сообществ (вне задания).
    """
    groups_list = Group.objects.all()
    context = {'groups': groups_list}
    template = 'posts/groups.html'
    return render(request, template, context)


def profile(request, username):
    """
    Отображение профиля пользователя.
    """
    author = get_object_or_404(User, username=username)
    # posts = author.posts.all()
    posts = author.posts.prefetch_related('author').all()
    paginator = Paginator(posts, settings.PAGINATOR_OBJECTS_PER_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    is_following = False
    show_follow_button = False
    # показывать кнопку подписки только для авторизованных
    # и на чужих страницах, на своей не надо
    # [TO-DO]: как вариант: кнопку подписки показывать для гостей,
    # но тогда с редиректом на авторизацию
    if request.user.is_authenticated and author != request.user:
        show_follow_button = True
        # проверка на подписки: True - [Подписаться], False - [Отписаться]
        if Follow.objects.filter(
                user=request.user).filter(author=author).exists():
            is_following = True
    context = {
        'author': author,
        'count': paginator.count,
        'following': is_following,
        'show_follow_button': show_follow_button,
        'page_obj': page_obj,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    """
    Отображение поста и информации о нём.
    """
    post = get_object_or_404(Post, id=post_id)
    # список групп сбоку в шаблоне
    group_list = Group.objects.all()
    # последние три поста сбоку в шаблоне
    post_list = Post.objects.filter()[:3]
    # комментарии к посту
    comments = post.comments.prefetch_related('author').all()
    form = CommentForm()
    context = {
        'post': post,
        'comments': comments,
        'groups': group_list,
        'posts': post_list,
        'form': form,
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    """
    Создание поста.
    Поле автора не включено на форме,
    а без него save не сохранит неполную модель,
    поэтому вручную определяем дополнительное обязательное поле.
    """
    form = PostForm(request.POST or None, files=request.FILES or None)
    if request.method == 'POST':
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('post:profile', username=request.user.username)
    context = {
        'form': form,
        'is_edit': False,
    }
    return render(request, 'posts/create_post.html', context)


@login_required
def post_edit(request, post_id):
    """
    Редактирование поста.
    """
    post = get_object_or_404(Post, id=post_id)
    # Если юзер не автор данного поста, редиректим
    if post.author != request.user:
        return redirect('post:post_detail', post_id=post_id)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post,
    )
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return redirect('post:post_detail', post_id=post_id)
    context = {
        # 'post': post,
        'form': form,
        'is_edit': True,
    }
    return render(request, 'posts/create_post.html', context)


@login_required
def add_comment(request, post_id):
    """
    Добавление комментария.
    """
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('post:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    """
    Страница с контентом автора, на которого подписан пользователь.
    """
    follows = Follow.objects.filter(user=request.user).values('author')
    following_posts = Post.objects.prefetch_related(
        'author').filter(author_id__in=follows)
    paginator = Paginator(following_posts, settings.PAGINATOR_OBJECTS_PER_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {'page_obj': page_obj}
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    """
    Подписка на контент автора.
    """
    author = get_object_or_404(User, username=username)
    # проверяем, что юзер ещё не подписан
    is_follow = Follow.objects.filter(
        user=request.user).filter(author=author).exists()
    # самого на себя не подписываем и если ещё не подписан
    # кнопки итак не должны отображаться, проверка от взлома
    if username != request.user.username and not is_follow:
        Follow.objects.create(user=request.user, author=author)
    return redirect('post:profile', username=username)


@login_required
def profile_unfollow(request, username):
    """
    Отписка от автора (от надоевшего графомана).
    """
    author = get_object_or_404(User, username=username)
    # проверяем, что юзер подписан
    is_follow = Follow.objects.filter(
        user=request.user).filter(author=author).exists()
    # самого себя не отписываем и если уже подписан
    if username != request.user.username and is_follow:
        Follow.objects.filter(user=request.user).filter(author=author).delete()
    return redirect('post:profile', username=username)
