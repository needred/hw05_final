# Проект "Yatube"
**Социальная сеть (аналог Twitter) с возможностью создания, просмотра, редактирования и удаления (CRUD) записей.**
* Реализован механизм подписки на понравившихся авторов и отслеживание их записей.
* Кастомизация страниц ошибок.
* Используется пагинация постов и кэширование.
* Реализована регистрация пользователей с верификацией данных, сменой и восстановлением пароля через почту.
* Покрытие тестами. Возможность добавления изображений.

### Технологический стек
[![Python](https://img.shields.io/badge/-Python-464646?style=for-the-badge&logo=Python&logoColor=56C0C0&color=008080)](https://www.python.org/) [![Django](https://img.shields.io/badge/-Django-464646?style=for-the-badge&logo=Django&logoColor=56C0C0&color=008080)](https://www.djangoproject.com/) [![Django ORM](https://img.shields.io/badge/-Django%20ORM-464646?style=for-the-badge&logo=Django&logoColor=56C0C0&color=008080)](https://docs.djangoproject.com/en/4.0/topics/db/models/) [![SQLite](https://img.shields.io/badge/-SQLite-464646?style=for-the-badge&logo=SQLite&logoColor=56C0C0&color=008080)](https://www.sqlite.org/index.html) [![pytest](https://img.shields.io/badge/-pytest-464646?style=for-the-badge&logo=Pytest&logoColor=56C0C0&color=008080)](https://docs.pytest.org/en/7.0.x/)

### Технические требования
1) Все необходимые пакеты перечислены в ```requirements.txt```

### Запуск приложения
1) Установите зависимости из ```requirements.txt```:
    - ```pip install -r requirements.txt```
2) После установки пакетов примените все необходимые миграции:
    - ```python manage.py makemigrations```
    - ```python manage.py migrate```
3) Для доступа к панели администратора создайте администратора:
    - ```python manage.py createsuperuser```
4) Запустите приложение:
    - ```python manage.py runserver```

### Пример работы сервиса
https://first.serveblog.net/
