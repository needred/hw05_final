from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

from ..models import Group, Post

User = get_user_model()

# вынес все пути в константы, т.к. востребованы в нескольких функциях
TEST_SLUG = 'test-slug'
SLUG_NONEXIST = 'non-existent'
USERNAME_AUTH = 'SherlockHolmes'
USER_NONEXIST = 'non-existent'
AUTH_LOGIN = reverse('users:login')
CREATE_POST = reverse('post:post_create')
GROUPS = reverse('post:group')
GROUP_POSTS = reverse('post:group_list', kwargs={'slug': TEST_SLUG})
INDEX = reverse('post:index')
PROFILE = reverse('post:profile', kwargs={'username': USERNAME_AUTH})
# несуществующий слаг, юзер, пост
GROUP_NONEXIST = reverse('post:group_list', kwargs={'slug': SLUG_NONEXIST})
PROFILE_NONEXIST = reverse('post:profile', kwargs={'username': USER_NONEXIST})
POST_NONEXIST = reverse('post:post_detail', kwargs={'post_id': 1000})

class PostsURLTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username=USERNAME_AUTH)
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug=TEST_SLUG,
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )
        cls.EDIT_POST_URL = reverse('post:post_edit',
                                    kwargs={'post_id': cls.post.id})
        cls.POST_URL = reverse('post:post_detail',
                               kwargs={'post_id': cls.post.id})

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='NoNameUser')
        # авторизованный автор поста
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        # авторизованный НЕ автор поста
        self.user_not_author = User.objects.create_user(
            username='DrJohnHWatson'
        )
        self.authorized_not_author_client = Client()
        self.authorized_not_author_client.force_login(self.user_not_author)

    def test_urls_uses_correct_template(self):
        """
        Проверка вызываемых шаблонов для каждого адреса
        для авторизованных и неавторизованных юзеров.
        """
        # кортеж из адресов, шаблонов и типа клиента
        url_names_templates = (
            (INDEX, 'posts/index.html', self.guest_client),
            (INDEX, 'posts/index.html', self.authorized_client),
            (GROUPS, 'posts/groups.html', self.guest_client),
            (GROUPS, 'posts/groups.html', self.authorized_client),
            (GROUP_POSTS, 'posts/group_list.html', self.guest_client),
            (GROUP_POSTS, 'posts/group_list.html', self.authorized_client),
            (PROFILE, 'posts/profile.html', self.guest_client),
            (PROFILE, 'posts/profile.html', self.authorized_client),
            (self.POST_URL, 'posts/post_detail.html', self.guest_client),
            (self.POST_URL, 'posts/post_detail.html', self.authorized_client),
            ('/unexisting_page/', 'errors/404.html', self.guest_client),
            ('/unexisting_page/', 'errors/404.html', self.authorized_client),
            (CREATE_POST, 'posts/create_post.html', self.authorized_client),
        )
        for address, template, client in url_names_templates:
            with self.subTest(adress=address):
                response = client.get(address)
                self.assertTemplateUsed(response, template)

    def test_urls_exists(self):
        """
        Проверка доступности страниц.
        """
        # кортеж из проверяемого url, возвращаемого статус-кода и типа клиента
        status_urls = (
            (INDEX, HTTPStatus.OK, self.guest_client),
            (INDEX, HTTPStatus.OK, self.authorized_client),
            (GROUPS, HTTPStatus.OK, self.guest_client),
            (GROUPS, HTTPStatus.OK, self.authorized_client),
            (GROUP_POSTS, HTTPStatus.OK, self.guest_client),
            (GROUP_POSTS, HTTPStatus.OK, self.authorized_client),
            (GROUP_NONEXIST, HTTPStatus.NOT_FOUND, self.guest_client),
            (GROUP_NONEXIST, HTTPStatus.NOT_FOUND, self.authorized_client),
            (PROFILE, HTTPStatus.OK, self.guest_client),
            (PROFILE, HTTPStatus.OK, self.authorized_client),
            (PROFILE_NONEXIST, HTTPStatus.NOT_FOUND, self.guest_client),
            (PROFILE_NONEXIST, HTTPStatus.NOT_FOUND, self.authorized_client),
            (self.POST_URL, HTTPStatus.OK, self.guest_client),
            (self.POST_URL, HTTPStatus.OK, self.authorized_client),
            (POST_NONEXIST, HTTPStatus.NOT_FOUND, self.guest_client),
            (POST_NONEXIST, HTTPStatus.NOT_FOUND, self.authorized_client),
            (CREATE_POST, HTTPStatus.FOUND, self.guest_client),
            (CREATE_POST, HTTPStatus.OK, self.authorized_client),
        )
        for address, status_code, client in status_urls:
            with self.subTest(adress=address):
                response = client.get(address)
                self.assertEqual(response.status_code, status_code)

    def test_post_redirect_correct_urls(self):
        """
        Проверка редиректов для пользователей.
        """
        # кортеж из проверяемого url, редиректа и типа клиента
        redirect_post_urls = (
            (CREATE_POST, f'{AUTH_LOGIN}?next={CREATE_POST}',
             self.guest_client),
            (self.EDIT_POST_URL, f'{AUTH_LOGIN}?next={self.EDIT_POST_URL}',
             self.guest_client),
            (self.EDIT_POST_URL, self.POST_URL,
             self.authorized_not_author_client),
        )
        for address, redirect, client in redirect_post_urls:
            with self.subTest(adress=address):
                response = client.get(address)
                self.assertRedirects(response, redirect)
