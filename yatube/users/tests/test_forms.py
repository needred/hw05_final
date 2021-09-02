from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse


User = get_user_model()

SIGNUP = reverse('users:signup')
LOGIN = reverse('users:login')
INDEX = reverse('post:index')
PSW_RESET_FORM = reverse('users:password_reset_form')
PSW_RESET_DONE = reverse('users:password_reset_done')
PSW_CHANGE_FORM = reverse('users:password_change_form')
PSW_CHANGE_DONE = reverse('users:password_change_done')


class UsersFormsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='SherlockHolmes')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.guest_client = Client()
        cls.user_guest = User.objects.create_user(username='NoNameUser')

    def test_signup_create_user(self):
        """
        Форма signup создает нового юзера.
        """
        # Подсчитаем количество юзеров
        users_count = User.objects.count()
        # Подготавливаем данные для передачи в форму
        form_data = {
            'first_name': 'James',
            'last_name': 'Moriarty',
            'username': 'professor',
            'email': 'prof.j.moriarty@london.uk',
            'password1': 'I_m_a_villain1891',
            'password2': 'I_m_a_villain1891',
        }
        response = self.guest_client.post(SIGNUP, data=form_data, follow=True)
        # Проверяем, сработал ли редирект
        self.assertRedirects(response, INDEX)
        # Проверяем, увеличилось ли число юзеров
        self.assertEqual(User.objects.count(), users_count + 1)
        # Проверяем, что создалась запись
        self.assertTrue(User.objects.filter(
            first_name='James',
            last_name='Moriarty',
            username='professor',
            email='prof.j.moriarty@london.uk',
        ).exists())
