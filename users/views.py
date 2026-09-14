from django.contrib import messages, auth
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import reverse
from users.forms import UserLoginForm, UserRegisterForm
from users.models import Profile

# Create your views here.


def login_view(request):
    if request.method == 'POST':
        print(request.POST)
        form = UserLoginForm(data=request.POST)
        if form.is_valid():
            username = request.POST['username']
            password = request.POST['password']

            user = auth.authenticate(username=username, password=password)

            if user and user.is_active:
                auth.login(request, user)
                return HttpResponseRedirect(reverse('users:account'))

    else:
        form = UserLoginForm()

    context = {
        "form": form,
    }
    return render(request, "users/login.html", context)


def register_view(request):
    if request.user.is_authenticated:
        return redirect('users:account')

    if request.method == 'POST':
        form = UserRegisterForm(data=request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('users:account')
    else:
        form = UserRegisterForm()

    context = {
        'title': 'Регистрация',
        'form': form,
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

    has_profile_data = bool(
        request.user.first_name or request.user.last_name or request.user.email or profile.phone
    )
    edit_section = request.GET.get('edit')

    context = {
        'title': 'Личный кабинет',
        'profile': profile,
        'profile_locked': has_profile_data and edit_section != 'profile',
        'password_locked': edit_section != 'password',
    }
    return render(request, "users/account.html", context)


@login_required(login_url='users:login')
def history_view(request):
    context = {
        'title': 'История покупок',
    }
    return render(request, "users/history.html", context)


@login_required(login_url='users:login')
def favorites_view(request):
    context = {
        'title': 'Избранное',
    }
    return render(request, "users/favorites.html", context)
