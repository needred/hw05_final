from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse
from django import forms

User = get_user_model()

SIGNUP = reverse('users:signup')
LOGOUT = reverse('users:logout')
LOGIN = reverse('users:login')
PSW_RESET_FORM = reverse('users:password_reset_form')
PSW_RESET_DONE = reverse('users:password_reset_done')
PSW_CHANGE_FORM = reverse('users:password_change_form')
PSW_CHANGE_DONE = reverse('users:password_change_done')


class UsersViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='SherlockHolmes')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.guest_client = Client()
        cls.user_guest = User.objects.create_user(username='NoNameUser')

    def test_user_pages_uses_correct_template(self):
        """
        Проверка использования view-классами ожидаемых HTML-шаблонов.
        """
        url_names_templates = (
            (PSW_RESET_FORM, 'users/password_reset_form.html',
             self.guest_client),
            (PSW_RESET_FORM, 'users/password_reset_form.html',
             self.authorized_client),
            (PSW_RESET_DONE, 'users/password_reset_done.html',
             self.guest_client),
            (PSW_RESET_DONE, 'users/password_reset_done.html',
             self.authorized_client),
            (PSW_CHANGE_FORM, 'users/password_change_form.html',
             self.authorized_client),
            (PSW_CHANGE_DONE, 'users/password_change_done.html',
             self.authorized_client),
            (SIGNUP, 'users/signup.html', self.guest_client),
            (LOGIN, 'users/login.html', self.guest_client),
            (LOGOUT, 'users/logout.html', self.authorized_client),
        )
        for address, template, client in url_names_templates:
            with self.subTest(template=template):
                response = client.get(address)
                self.assertTemplateUsed(response, template)

    def test_user_signup_uses_correct_template(self):
        """
        Шаблон signup сформирован с правильным контентом.
        """
        response = self.guest_client.get(SIGNUP)
        form_fields = {
            'first_name': forms.fields.CharField,
            'last_name': forms.fields.CharField,
            'username': forms.fields.CharField,
            'email': forms.fields.EmailField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)
