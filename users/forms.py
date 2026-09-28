from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from users.models import User


def get_password_errors(password, user=None):
    """Встроенные проверки Django из AUTH_PASSWORD_VALIDATORS (settings.py):
    не короче 8 символов, не похож на логин/почту, не из списка простых, не только цифры.
    Возвращает список текстов ошибок (пустой, если пароль подходит)."""
    try:
        validate_password(password, user)
    except ValidationError as error:
        return list(error.messages)
    return []

class UserLoginForm(AuthenticationForm):

    class Meta:
        model = User
        fields = ('username', "password")


class UserRegisterForm(forms.ModelForm):
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Повторите пароль', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'password2')

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('Пользователь с таким именем уже существует')
        return username

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password2 = cleaned_data.get('password2')
        if password and password2 and password != password2:
            self.add_error('password2', 'Пароли не совпадают')
        if password:
            # пользователь ещё не создан, но логин и почта уже известны — для проверки «пароль похож на логин»
            candidate = User(username=cleaned_data.get('username'), email=cleaned_data.get('email'))
            for error in get_password_errors(password, candidate):
                self.add_error('password', error)
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user