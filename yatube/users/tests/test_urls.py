from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

User = get_user_model()

SIGNUP = reverse('users:signup')
LOGOUT = reverse('users:logout')
LOGIN = reverse('users:login')
PSW_RESET_FORM = reverse('users:password_reset_form')
PSW_RESET_DONE = reverse('users:password_reset_done')
PSW_CHANGE_FORM = reverse('users:password_change_form')
PSW_CHANGE_DONE = reverse('users:password_change_done')


class UsersURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='SherlockHolmes')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.guest_client = Client()
        cls.user_guest = User.objects.create_user(username='NoNameUser')

    def test_user_urls_uses_correct_template(self):
        """
        Проверка вызываемых users шаблонов для каждого адреса.
        """
        url_names_templates = (
            (PSW_CHANGE_FORM, 'users/password_change_form.html',
             self.authorized_client),
            (PSW_CHANGE_DONE, 'users/password_change_done.html',
             self.authorized_client),
            (PSW_RESET_FORM, 'users/password_reset_form.html',
             self.guest_client),
            (PSW_RESET_FORM, 'users/password_reset_form.html',
             self.authorized_client),
            (PSW_RESET_DONE, 'users/password_reset_done.html',
             self.guest_client),
            (PSW_RESET_DONE, 'users/password_reset_done.html',
             self.authorized_client),
            (SIGNUP, 'users/signup.html', self.guest_client),
            (LOGIN, 'users/login.html', self.guest_client),
            (LOGOUT, 'users/logout.html', self.authorized_client),
        )
        for address, template, client in url_names_templates:
            with self.subTest(adress=address):
                response = client.get(address)
                self.assertTemplateUsed(response, template)

    def test_users_urls_exists(self):
        """
        Проверка доступности users страниц.
        """
        status_urls = (
            (PSW_RESET_FORM, HTTPStatus.OK, self.guest_client),
            (PSW_RESET_FORM, HTTPStatus.OK, self.authorized_client),
            (PSW_CHANGE_FORM, HTTPStatus.FOUND, self.guest_client),
            (PSW_CHANGE_FORM, HTTPStatus.FOUND, self.authorized_client),
            (SIGNUP, HTTPStatus.OK, self.guest_client),
            (LOGIN, HTTPStatus.OK, self.guest_client),
            (LOGOUT, HTTPStatus.OK, self.authorized_client),
        )
        for address, status_code, client in status_urls:
            with self.subTest(adress=address):
                response = client.get(address)
                self.assertEqual(response.status_code, status_code)

    def test_users_redirect_correct_urls(self):
        """
        Проверка редиректов для пользователей.
        """
        redirect_post_urls = (
            (PSW_CHANGE_FORM, f'{LOGIN}?next={PSW_CHANGE_FORM}',
             self.guest_client),
        )
        for address, redirect, client in redirect_post_urls:
            with self.subTest(adress=address):
                response = client.get(address)
                self.assertRedirects(response, redirect)
