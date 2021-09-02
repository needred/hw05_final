from django.contrib import admin

from .models import Group, Post


class PostAdmin(admin.ModelAdmin):
    """
    Параметры отображения модели Post (посты)
    в интерфейсе администратора.
    """
    list_display = ('pk', 'text', 'pub_date', 'author', 'group')
    search_fields = ('text',)
    list_filter = ('pub_date',)
    empty_value_display = '-пусто-'
    list_editable = ('group',)


class GroupAdmin(admin.ModelAdmin):
    """
    Параметры отображения модели Group (сообщества)
    в интерфейсе администратора.
    """
    list_display = ('pk', 'title', 'slug', 'description')
    search_fields = ('description',)
    list_filter = ('title',)
    empty_value_display = '-пусто-'


admin.site.register(Group, GroupAdmin)
admin.site.register(Post, PostAdmin)
