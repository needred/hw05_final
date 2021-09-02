from os import path
import shutil
import tempfile

from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import tag, TestCase, Client, override_settings
from django.urls import reverse

from time import sleep

from ..models import Group, Post, Comment

User = get_user_model()

TEST_SLUG = 'test-slug'
TEST_SLUG_2 = 'test-slug-2'
USERNAME_AUTH = 'SherlockHolmes'
CREATE_POST = reverse('post:post_create')
GROUPS = reverse('post:group')
GROUP_POSTS = reverse('post:group_list', kwargs={'slug': TEST_SLUG})
OTHER_GROUP_POSTS = reverse('post:group_list', kwargs={'slug': TEST_SLUG_2})
INDEX = reverse('post:index')
PROFILE = reverse('post:profile', kwargs={'username': USERNAME_AUTH})
TEST_POST = 'Тестовый пост. Давным-давно, в далёкой-далёкой галактике...'
IMG_NAME = 'small.gif'
POSTS_IMG = path.join(Post._meta.app_label, IMG_NAME).replace('\\', '/')
# Создаем временную папку для медиа-файлов;
# на момент теста медиа папка будет переопределена
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


# Для сохранения media-файлов в тестах будет использоваться
# временная папка TEMP_MEDIA_ROOT, а потом мы ее удалим
@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostsViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username=USERNAME_AUTH)
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug=TEST_SLUG,
            description='Тестовое описание',
        )
        # Другая группа для проверки постов на страницах групп
        Group.objects.create(
            title='Тестовая группа 2',
            slug=TEST_SLUG_2,
            description='Тестовое описание 2',
        )
        # Пост без группы для проверки отображения.
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост без сообщества.',
            group=None,
        )
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00'
            b'\x01\x00\x00\x00\x00\x21\xf9\x04'
            b'\x01\x0a\x00\x01\x00\x2c\x00\x00'
            b'\x00\x00\x01\x00\x01\x00\x00\x02'
            b'\x02\x4c\x01\x00\x3b'
        )
        uploaded = SimpleUploadedFile(
            name=IMG_NAME,
            content=small_gif,
            content_type='image/gif',
        )
        # Задержка, чтобы даты были гарантированно разными,
        # так как могут создаться почти одновременно.
        sleep(0.1)
        cls.post = Post.objects.create(
            author=cls.user,
            text=TEST_POST,
            group=cls.group,
            image=uploaded,
        )
        Comment.objects.create(
            author=cls.user,
            post=cls.post,
            text='Комментарий 1',
        )
        cls.EDIT_POST_URL = reverse('post:post_edit',
                                    kwargs={'post_id': cls.post.id})
        cls.POST_URL = reverse('post:post_detail',
                               kwargs={'post_id': cls.post.id})
        cls.guest_client = Client()
        cls.user_guest = User.objects.create_user(username='NoNameUser')

    @classmethod
    def tearDownClass(cls):
        # Метод shutil.rmtree удаляет директорию и всё её содержимое
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    # Из документации попробовал теги для выборочного запуска тестов - удобно!
    # test posts.tests.test_views --tag=index
    @tag('index', 'group', 'profile', 'post')
    def test_pages_uses_correct_template(self):
        """
        Проверка использования view-классами ожидаемых HTML-шаблонов.
        """
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
        )
        for address, template, client in url_names_templates:
            with self.subTest(template=template):
                response = client.get(address)
                self.assertTemplateUsed(response, template)

    @tag('index')
    def test_index_show_correct_context(self):
        """
        Шаблон index сформирован с правильным контекстом.
        """
        response = self.authorized_client.get(INDEX)
        post_text_0 = response.context.get('page_obj')[0].text
        post_author_0 = response.context.get('page_obj')[0].author.username
        post_group_0 = response.context.get('page_obj')[0].group.id
        post_image_0 = response.context.get('page_obj')[0].image
        self.assertEqual(post_text_0, TEST_POST)
        self.assertEqual(post_author_0, USERNAME_AUTH)
        self.assertEqual(post_group_0, self.group.id)
        self.assertEqual(post_image_0, POSTS_IMG)

    @tag('group')
    def test_group_list_show_correct_context(self):
        """
        Шаблон group сформирован с правильным контекстом.
        """
        response = self.authorized_client.get(GROUP_POSTS)
        self.assertEqual(response.context.get('group').title,
                         'Тестовая группа')
        self.assertEqual(response.context.get('group').description,
                         'Тестовое описание')
        self.assertEqual(response.context.get('group').slug, TEST_SLUG)
        post_image_0 = response.context.get('page_obj')[0].image
        self.assertEqual(post_image_0, POSTS_IMG)

    @tag('profile')
    def test_profile_show_correct_context(self):
        """
        Шаблон profile сформирован с правильным контекстом.
        """
        response = self.authorized_client.get(PROFILE)
        self.assertEqual(response.context.get('count'), 2)
        self.assertEqual(response.context.get('author').username,
                         USERNAME_AUTH)
        self.assertEqual(len(response.context.get('page_obj').object_list),
                         2, 'Неверное количество постов на странице')
        post_image_0 = response.context.get('page_obj')[0].image
        self.assertEqual(post_image_0, POSTS_IMG)

    def test_edit_post_show_correct_context(self):
        """
        Шаблон post_edit сформирован с правильным контекстом.
        """
        response = self.authorized_client.get(self.EDIT_POST_URL)
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
            'image': forms.fields.ImageField,
        }
        for form_label, expected in form_fields.items():
            with self.subTest(value=form_label):
                field = response.context.get('form').fields.get(form_label)
                self.assertIsInstance(field, expected)
        self.assertTrue(response.context.get('is_edit'),
                        'В контексте post_edit установлено is_edit==False')

    @tag('post')
    def test_post_show_correct_context(self):
        """
        Шаблон post сформирован с правильным контекстом.
        """
        response = self.authorized_client.get(self.POST_URL)
        self.assertIn('post', response.context)
        self.assertIn('form', response.context)
        post_context = {
            response.context['post'].text: self.post.text,
            response.context['post'].author.username: self.user.username,
            response.context['post'].image: POSTS_IMG,
            response.context.get('comments')[0].text: 'Комментарий 1',
        }
        for key, value in post_context.items():
            with self.subTest(key=key, value=value):
                self.assertEqual(key, value)

    @tag('group')
    def test_groups_show_correct_context(self):
        """
        На странице со списком сообществ показано правильное количество групп.
        """
        # страница сл списком сообществ - вне задания
        response = self.authorized_client.get(GROUPS)
        self.assertEqual(len(response.context.get('groups')), 2)

    @tag('group')
    def test_post_view_on_your_group_page(self):
        """
        Пост с выбранным сообществом появляется только на странице этой группы.
        """
        response = self.authorized_client.get(GROUP_POSTS)
        self.assertEqual(len(response.context.get('page_obj').object_list), 1)
        self.assertEqual(response.context.get('page_obj')[0].text, TEST_POST)

    @tag('group')
    def test_post_view_on_other_group_page(self):
        """
        Пост с выбранным сообществом НЕ появляется на странице другой группы.
        """
        response = self.authorized_client.get(OTHER_GROUP_POSTS)
        self.assertEqual(len(response.context.get('page_obj').object_list), 0)

    def test_cache_index_page(self):
        """
        Кэширование главной страницы при добавлениии поста.
        """
        response_cache = self.guest_client.get(INDEX)
        Post.objects.create(
            text='Ещё один пост для проверки кэша.',
            author=self.user,
            group=None,
        )
        response_after_add = self.guest_client.get(INDEX)
        self.assertEqual(response_cache.content,
                         response_after_add.content,
                         msg='Кэш не работает - разный контент')
        # очищаем кэш для проверки обновления контента
        cache.clear()
        response_cache_refresh = self.guest_client.get(INDEX)
        self.assertNotEqual(response_cache.content,
                            response_cache_refresh.content,
                            msg='После сброса кэша - одинаковый контент')

    def test_cache(self):
        """
        Кэширование главной страницы при удалении поста.
        """
        cache_before_delete = self.guest_client.get(INDEX)
        Post.objects.all().delete()
        cached_after_delete = self.guest_client.get(INDEX)
        cache.clear()
        actual_cache = self.guest_client.get(INDEX)
        self.assertEqual(
            cache_before_delete.content, cached_after_delete.content,
            msg='Кэш не работает - разный контент'
        )
        self.assertNotEqual(
            cache_before_delete.content, actual_cache.content,
            msg='После сброса кэша - одинаковый контент'
        )


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.USERNAME = 'MrsHudson'
        cls.user = User.objects.create_user(username=cls.USERNAME)
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug=TEST_SLUG,
            description='Тестовое описание',
        )
        # Генерируем несколько постов для проверки пагинатора по формуле:
        # кол-во постов на странице (из настроек пагинатора) плюс ещё половина.
        posts = [
            Post(author=cls.user, text=f'Тестовый пост {i}', group=cls.group)
            for i in range(settings.PAGINATOR_OBJECTS_PER_PAGE
                           + int(settings.PAGINATOR_OBJECTS_PER_PAGE / 2))
        ]
        Post.objects.bulk_create(posts)
        cls.GROUP_POSTS = reverse('post:group_list',
                                  kwargs={'slug': TEST_SLUG})
        cls.PROFILE = reverse('post:profile',
                              kwargs={'username': cls.USERNAME})

    def test_page_contains_posts(self):
        """
        Проверка количества постов на страницах с пагинатором.
        """
        list_urls = [INDEX, self.GROUP_POSTS, self.PROFILE]
        page_count = {
            1: settings.PAGINATOR_OBJECTS_PER_PAGE,
            2: int(settings.PAGINATOR_OBJECTS_PER_PAGE / 2)
        }
        for page in list_urls:
            for pagenum, post_count in page_count.items():
                with self.subTest(page=page):
                    # Проверка количества постов на указанной странице
                    response = self.authorized_client.get(
                        page, {'page': pagenum}
                    )
                    self.assertEqual(
                        len(response.context.get('page_obj').object_list),
                        post_count
                    )
