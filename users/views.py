from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import redirect, render
from users.models import Profile

# Create your views here.


def login_view(request):
    if request.user.is_authenticated:
        return redirect('users:account')

    error = None
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('users:account')
        error = 'Неверный логин или пароль'

    context = {
        'title': 'Вход',
        'error': error,
    }
    return render(request, "users/login.html", context)


def register_view(request):
    if request.user.is_authenticated:
        return redirect('users:account')

    error = None
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        password2 = request.POST.get('password2', '')

        if not username or not password:
            error = 'Заполните обязательные поля'
        elif password != password2:
            error = 'Пароли не совпадают'
        elif User.objects.filter(username=username).exists():
            error = 'Пользователь с таким именем уже существует'
        else:
            user = User.objects.create_user(username=username, email=email, password=password)
            login(request, user)
            return redirect('users:account')

    context = {
        'title': 'Регистрация',
        'error': error,
    }
    return render(request, "users/register.html", context)


def logout_view(request):
    logout(request)
    return redirect('index')


@login_required(login_url='users:login')
def account_view(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form_type = request.POST.get('form')

        if form_type == 'profile':
            request.user.first_name = request.POST.get('first_name', '').strip()
            request.user.last_name = request.POST.get('last_name', '').strip()
            request.user.email = request.POST.get('email', '').strip()
            request.user.save()

            profile.phone = request.POST.get('phone', '').strip()
            profile.save()

            messages.success(request, 'Данные профиля сохранены')
            return redirect('users:account')

        elif form_type == 'password':
            old_password = request.POST.get('old_password', '')
            new_password = request.POST.get('new_password', '')
            new_password2 = request.POST.get('new_password2', '')

            if not request.user.check_password(old_password):
                messages.error(request, 'Текущий пароль указан неверно')
            elif new_password != new_password2:
                messages.error(request, 'Новые пароли не совпадают')
            elif len(new_password) < 8:
                messages.error(request, 'Новый пароль должен быть не короче 8 символов')
            else:
                request.user.set_password(new_password)
                request.user.save()
                update_session_auth_hash(request, request.user)
                messages.success(request, 'Пароль изменён')
            return redirect('users:account')

    context = {
        'title': 'Личный кабинет',
        'profile': profile,
    }
    return render(request, "users/account.html", context)
