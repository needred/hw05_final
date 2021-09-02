from datetime import datetime
from django import template

register = template.Library()


@register.filter
def days_until(date):
    """
    Вычисление разницы между датами создания постов.
    Чтобы показывать плашку "Новое" только на свежих постах.
    """
    delta = datetime.now().date() - datetime.date(date)
    return delta.days


@register.filter
def first_2paragraph(value):
    """
    Обрезка текста поста до первых двух абзацев.
    """
    paragraphs = value.split('\n')
    # return len(paragraphs)
    return '\n'.join(paragraphs[:4])
