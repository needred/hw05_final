from django.views.generic import CreateView
from django.urls import reverse_lazy
from .forms import CreationForm


class SignUp(CreateView):
    """
    Отображение пользовательской формы регистрации.
    """
    form_class = CreationForm
    success_url = reverse_lazy('post:index')
    template_name = 'users/signup.html'
