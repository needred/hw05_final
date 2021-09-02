from django.contrib.auth import get_user_model
from django.db import models
from django.db.models.constraints import UniqueConstraint

User = get_user_model()


class Group(models.Model):
    """
    Модель сообществ.
    title - название сообщества
    slug - идентификатор в URL
    description - описание.
    """
    title = models.CharField(
        max_length=200,
        null=True,
        verbose_name='Название сообщества',
    )
    slug = models.SlugField(
        max_length=200,
        unique=True,
        null=True,
        verbose_name='Адрес',
        help_text='Придумайте уникальный URL адрес для страницы сообщества',
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name='Описание',
        help_text='Введите описание',
    )

    class Meta:
        verbose_name = 'Сообщество'
        verbose_name_plural = 'Сообщества'

    def __str__(self):
        return self.title


class Post(models.Model):
    """
    Модель для постов в соцсети.
    text - текст поста
    pub_date - дата публикации
    author - автор поста
    group - ссылка на сообщество
    image - картинка к посту.
    """
    text = models.TextField(
        verbose_name='Текст',
        help_text='Текст вашего поста',
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор',
    )
    group = models.ForeignKey(
        Group, blank=True, null=True,
        on_delete=models.SET_NULL,
        related_name='posts',
        verbose_name='Сообщество',
        help_text='Группа, к которой будет относиться пост',
    )
    image = models.ImageField(
        verbose_name='Изображение',
        upload_to='posts/',
        blank=True,
        help_text='Картинка к посту',
    )

    class Meta:
        ordering = ['-pub_date']
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'

    def __str__(self):
        return self.text[:15]


class Comment(models.Model):
    """
    Модель для комментариев.
    post - комментируемый пост
    author - автор комментария
    text - текст комментария
    created - дата комментирования.
    """
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE,
        verbose_name='Пост',
        related_name='comments',
        help_text='Какой пост комментируем?',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор',
    )
    text = models.TextField(
        verbose_name='Комментарий',
        help_text='Текст комментария',
    )
    created = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата комментирования',
    )

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self):
        return self.text


class Follow(models.Model):
    """
    Модель для подписок.
    user - подписчик
    author - автор, на которого подписываются.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор'
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        # Не задумывался о необходимости создания уникальных ограничений в БД
        # но увидел, что ревьюеры делают замечание сокурсникам по этому поводу
        UniqueConstraint(fields=['user', 'author'], name='follow_unique')
