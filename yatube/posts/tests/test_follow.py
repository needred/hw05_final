from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Post, Follow

User = get_user_model()

USERNAME_AUTH = 'SherlockHolmes'
INDEX = reverse('post:index')
PROFILE = reverse('post:profile', kwargs={'username': USERNAME_AUTH})
FOLLOW_INDEX = reverse('post:follow_index')
FOLLOW = reverse('post:profile_follow', kwargs={'username': USERNAME_AUTH})
UNFOLLOW = reverse('post:profile_unfollow', kwargs={'username': USERNAME_AUTH})


class FollowTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username=USERNAME_AUTH)
        cls.follower = User.objects.create_user(username='Moriarty')
        cls.post = Post.objects.create(text='Тестовый пост 1',
                            author=cls.author,
                            group=None)
        cls.post2 = Post.objects.create(text='Тестовый пост 2',
                            author=cls.follower,
                            group=None)

    def setUp(self):
        self.authorized_author = Client()
        self.authorized_author.force_login(self.author)

        self.authorized_follower = Client()
        self.authorized_follower.force_login(self.follower)

        self.guest_client = Client()
        self.user_guest = User.objects.create_user(username='NoNameUser')

    def test_follow_urls_exists(self):
        """
        Проверка доступности страниц.
        """
        status_urls = (
            (FOLLOW, HTTPStatus.FOUND, self.authorized_author),
            (FOLLOW, HTTPStatus.FOUND, self.authorized_follower),
            (FOLLOW, HTTPStatus.FOUND, self.guest_client),
            (FOLLOW_INDEX, HTTPStatus.OK, self.authorized_author),
            (FOLLOW_INDEX, HTTPStatus.OK, self.authorized_follower),
            (FOLLOW_INDEX, HTTPStatus.FOUND, self.guest_client),
            (UNFOLLOW, HTTPStatus.FOUND, self.authorized_author),
            (UNFOLLOW, HTTPStatus.FOUND, self.authorized_follower),
            (UNFOLLOW, HTTPStatus.FOUND, self.guest_client),
        )
        for address, status_code, client in status_urls:
            with self.subTest(adress=address):
                response = client.get(address)
                self.assertEqual(response.status_code, status_code)

    def test_follow(self):
        """
        Проверка возможности подписаться на другого пользователя.
        """
        # follower подписывается на author
        profile_follow = self.authorized_follower.get(FOLLOW, follow=True)
        self.assertEqual(profile_follow.status_code, 200,
                         'Не удалось получить страницу после подписки')
        # проверка: у follower появилась подписка, у author нет подписки
        follower = self.authorized_follower.get(FOLLOW_INDEX)
        author = self.authorized_author.get(FOLLOW_INDEX)
        self.assertEqual(follower.status_code, 200,
                         'Фолловер после подписки не увидел страницу')
        self.assertEqual(author.status_code, 200,
                         'Автор после подписки не увидел страницу')
        self.assertIsInstance(follower.context.get('page_obj')[0], Post)
        test_message = follower.context.get('page_obj')[0].text
        self.assertEqual(test_message, 'Тестовый пост 1')
        # должен появиться список с автором в контексте страницы
        # self.assertEqual(follower.context.get('authors'), [2])

    def test_unfollow(self):
        """
        Проверка возможности отписаться от того, на кого подписан.
        """
        # отписываем follower от author
        profile_unfollow = self.authorized_follower.get(UNFOLLOW, follow=True)
        self.assertEqual(profile_unfollow.status_code, 200,
                         'Фолловер без подписок не увидел страницу')
        follower = self.authorized_follower.get(FOLLOW_INDEX)
        # список постов отписанного автора должен стать пустым
        self.assertEqual(len(follower.context.get('page_obj').object_list), 0,
                         'Список постов отписанного автора не пустой')

    def test_view_post_followed_users(self):
        """
        Новая запись пользователя ПОявляется в ленте подписчиков.
        """
        profile_follow = self.authorized_follower.get(FOLLOW, follow=True)
        context_follower = profile_follow.context['page_obj']
        self.assertIn(self.post, context_follower)

    def test_do_not_view_post_unfollowed_users(self):
        """
        Новая запись пользователя НЕ появляется в ленте НЕподписанных.
        """
        profile_nonfollow = self.authorized_author.get(FOLLOW, follow=True)
        context_nonfollower = profile_nonfollow.context['page_obj']
        self.assertNotIn(self.post2, context_nonfollower)