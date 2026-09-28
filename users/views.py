from django.contrib import messages, auth
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST
from products.models import Product
from users.forms import UserLoginForm, UserRegisterForm, get_password_errors
from users.models import Basket, Favorite, Order, Profile

# Create your views here.


def login_view(request):
    if request.method == 'POST':
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
            elif password_errors := get_password_errors(new_password, request.user):
                for error in password_errors:
                    messages.error(request, error)
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
    orders = Order.objects.filter(user=request.user).prefetch_related('items__product')
    context = {
        'title': 'История покупок',
        'orders': orders,
    }
    return render(request, "users/history.html", context)


@login_required(login_url='users:login')
def favorites_view(request):
    favorites = Favorite.objects.filter(user=request.user).select_related('product').order_by('-created')
    basket_product_ids = set(Basket.objects.filter(user=request.user).values_list('product_id', flat=True))
    context = {
        'title': 'Избранное',
        'favorites': favorites,
        'basket_product_ids': basket_product_ids,
    }
    return render(request, "users/favorites.html", context)


@login_required(login_url='users:login')
@require_POST
def favorite_toggle(request, product_id):
    # Одна кнопка-сердечко: если товар уже в избранном — убираем, иначе добавляем
    product = get_object_or_404(Product, id=product_id)
    favorite = Favorite.objects.filter(user=request.user, product=product)

    if favorite.exists():
        favorite.delete()
    else:
        Favorite.objects.create(user=request.user, product=product)

    return redirect_back(request, product.id)


@login_required(login_url='users:login')
def basket_view(request):
    baskets = Basket.objects.filter(user=request.user).select_related('product')
    context = {
        'title': 'Корзина',
        'baskets': baskets,
        'total_quantity': sum(basket.quantity for basket in baskets),
        'total_sum': sum(basket.sum() for basket in baskets),
    }
    return render(request, "users/basket.html", context)


def get_back_url(request):
    # Страница, где пользователь нажал кнопку. Если браузер её не передал или это чужой сайт — корзина.
    url = request.META.get('HTTP_REFERER', '')
    if not url_has_allowed_host_and_scheme(url, allowed_hosts={request.get_host()}):
        return reverse('users:basket')
    return url.split('#')[0]    # старый #product-N убираем, чтобы якоря не накапливались


def redirect_back(request, product_id):
    # Возвращаем пользователя на страницу, где он нажал кнопку,
    # и прокручиваем к карточке товара (#product-5)
    return HttpResponseRedirect(f'{get_back_url(request)}#product-{product_id}')


@login_required(login_url='users:login')
@require_POST
def basket_add(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    basket = Basket.objects.filter(user=request.user, product=product)

    if not basket.exists():
        Basket.objects.create(user=request.user, product=product, quantity=1)
    else:
        basket = basket.first()
        basket.quantity += 1
        basket.save()

    return redirect_back(request, product.id)


@login_required(login_url='users:login')
@require_POST
def basket_decrease(request, basket_id):
    basket = get_object_or_404(Basket, id=basket_id, user=request.user)

    if basket.quantity > 1:
        basket.quantity -= 1
        basket.save()
    else:
        basket.delete()

    return redirect_back(request, basket.product_id)


@login_required(login_url='users:login')
@require_POST
def basket_remove(request, basket_id):
    basket = get_object_or_404(Basket, id=basket_id, user=request.user)
    basket.delete()

    return HttpResponseRedirect(get_back_url(request))
