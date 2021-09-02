from os import path
import shutil
import tempfile

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..models import Post, Group, Comment

User = get_user_model()

TEST_SLUG = 'test-slug'
USERNAME_AUTH = 'SherlockHolmes'
CREATE_POST = reverse('post:post_create')
PROFILE = reverse('post:profile', kwargs={'username': USERNAME_AUTH})
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
IMG_NAME = 'small.gif'
POSTS_IMG = path.join(Post._meta.app_label, IMG_NAME).replace('\\', '/')


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostsFormsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username=USERNAME_AUTH)
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug=TEST_SLUG,
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.author,
            text='Тестовый пост',
            group=cls.group,
        )
        cls.comment = Comment.objects.create(
            text='Тестовый комментарий',
            author=cls.author,
            post=cls.post,
        )
        cls.EDIT_POST_URL = reverse('post:post_edit',
                                    kwargs={'post_id': cls.post.id})
        cls.POST_URL = reverse('post:post_detail',
                               kwargs={'post_id': cls.post.id})
        cls.ADD_COMMENT = reverse('post:add_comment',
                                  kwargs={'post_id': cls.post.id})

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.author)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def test_create_post_form(self):
        """
        Форма создаёт новый пост.
        """
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
            content_type='image/gif'
        )
        # сохраняем список постов до добавления
        posts_before_add = list(Post.objects.values_list('id', flat=True))
        form_data = {
            'text': 'Второй тестовый пост',
            'group': self.group.id,
            'image': uploaded,
        }
        response = self.authorized_client.post(
            CREATE_POST, data=form_data, follow=True,
        )
        # Проверяем, сработал ли редирект
        self.assertRedirects(response, PROFILE)
        # находим новый пост, исключая те что уже были
        new_post = Post.objects.exclude(id__in=posts_before_add)
        self.assertEqual(new_post.count(), 1)
        self.assertTrue(
            Post.objects.filter(
                text=form_data['text'],
                group=form_data['group'],
                image=POSTS_IMG,
            ).exists()
        )

    def test_edit_post_form(self):
        """
        Проверка редактирования поста - должна измениться
        соответствующая запись в БД.
        """
        form_data = {'text': 'Новый текст', 'group': self.group.id}
        self.authorized_client.post(self.EDIT_POST_URL, data=form_data)
        response = self.authorized_client.get(self.POST_URL)
        self.assertEqual(response.context.get('post').text, 'Новый текст')
        self.assertTrue(Post.objects.filter(
            text='Новый текст',
            group=self.group.id
        ).exists())

    def test_create_comment_form(self):
        """
        Форма создаёт новый комментарий.
        """
        # Алексей, спасибо за подсказку по values_list.
        # Я как-то совсем не сообразил использовать такой подход,
        # хотя подсознательно понимал, что с множествами перемудрил. ;)
        # сохраняем список комментариев до добавления
        comments_before_add = list(Comment.objects.values_list('id',
                                                               flat=True))
        form_data = {
            'text': 'Новый комментарий',
            'post': self.post.id,
            'author': self.author,
        }
        response = self.authorized_client.post(
            self.ADD_COMMENT, data=form_data, follow=True,
        )
        # Проверяем, сработал ли редирект
        self.assertRedirects(response, self.POST_URL)
        # находим новый комментарий
        new_comment = Comment.objects.exclude(id__in=comments_before_add)
        self.assertEqual(new_comment.count(), 1)
        self.assertTrue(
            Comment.objects.filter(
                text=form_data['text'],
                post=form_data['post'],
                author=form_data['author'],
            ).exists()
        )
