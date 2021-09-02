from django import forms
from .models import Post, Comment


class PostForm(forms.ModelForm):
    """
    Форма для редактирования и создания поста.
    """
    class Meta:
        model = Post
        fields = ('text', 'group', 'image')
        labels = {
            'text': 'Текст',
            'group': 'Сообщество',
            'image': 'Изображение',
        }
        help_texts = {
            'text': 'Текст вашего поста',
            'group': 'Группа, к которой будет относиться пост',
            'image': 'Картинка к посту',
        }


class CommentForm(forms.ModelForm):
    """
    Форма для добавления комментария.
    """
    class Meta:
        model = Comment
        fields = ('text',)
        labels = {
            'text': 'Комментарий',
        }
        help_texts = {
            'text': 'Текст комментария',
        }
