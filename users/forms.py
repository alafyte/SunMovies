from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

input_style = "bg-gray-50 border border-gray-300 text-gray-900 sm:text-sm rounded-lg focus:ring-primary-600 " \
              "focus:border-primary-600 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 " \
              "dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500"


class RegisterUserForm(UserCreationForm):
    username = forms.CharField(label="Логин", widget=forms.TextInput(attrs={'class': input_style}))
    email = forms.EmailField(label="Email", widget=forms.EmailInput(attrs={'class': input_style}))
    password1 = forms.CharField(label="Пароль", widget=forms.PasswordInput(attrs={'class': input_style}))
    password2 = forms.CharField(label="Повторите пароль", widget=forms.PasswordInput(attrs={'class': input_style}))

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise ValidationError("Email уже занят")
        return email

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


class LoginUserForm(AuthenticationForm):
    username = forms.CharField(label="Логин или e-mail", widget=forms.TextInput(attrs={'class': input_style}))
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput(attrs={'class': input_style}))
