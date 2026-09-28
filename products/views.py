from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Max, Min, Sum

from products.models import Product, ProductCategory
from users.models import Basket, Favorite
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

# Create your views here.

PRODUCTS_PER_PAGE = 12

# id категории → список (поле модели, заголовок группы).
# Группы выводятся на странице в этом же порядке.
CATEGORY_FILTERS = {
    1: [  # видеокарты
        ('brand', 'Производитель'),
        ('chip_vendor', 'Производитель чипа'),
        ('series', 'Серия'),
        ('memory', 'Объём видеопамяти, ГБ'),
        ('memory_type', 'Тип видеопамяти'),
        ('bus_width', 'Разрядность шины, бит'),
        ('pcie', 'Версия PCI Express'),
        ('rgb', 'Подсветка'),
        ('color', 'Цвет'),
    ],
    2: [  # процессоры
        ('brand', 'Производитель'),
        ('series', 'Серия'),
        ('socket', 'Сокет'),
        ('cores', 'Количество ядер'),
        ('threads', 'Количество потоков'),
        ('integrated_graphics', 'Встроенная графика'),
        ('tdp', 'Тепловыделение, Вт'),
        ('memory_type', 'Тип памяти'),
        ('package', 'Комплектация'),
    ],
    3: [  # материнские платы
        ('brand', 'Производитель'),
        ('socket', 'Сокет'),
        ('chipset', 'Чипсет'),
        ('form_factor', 'Форм-фактор'),
        ('memory_type', 'Тип памяти'),
        ('memory_slots', 'Слотов памяти'),
        ('wifi', 'Wi-Fi'),
    ],
    4: [  # оперативная память
        ('brand', 'Производитель'),
        ('memory_type', 'Тип памяти'),
        ('memory', 'Объём комплекта, ГБ'),
        ('modules', 'Модулей в комплекте'),
        ('frequency', 'Частота, МГц'),
        ('latency', 'Задержка (CL)'),
        ('form_factor', 'Форм-фактор'),
        ('rgb', 'Подсветка'),
        ('color', 'Цвет'),
    ],
    5: [  # хранение данных
        ('drive_type', 'Тип накопителя'),
        ('brand', 'Производитель'),
        ('capacity', 'Объём, ГБ'),
        ('interface', 'Интерфейс'),
        ('form_factor', 'Форм-фактор'),
    ],
    6: [  # охлаждение процессора
        ('cooling_type', 'Тип охлаждения'),
        ('brand', 'Производитель'),
        ('tdp', 'Рассеиваемая мощность, Вт'),
        ('fan_size', 'Размер вентилятора, мм'),
        ('rgb', 'Подсветка'),
        ('color', 'Цвет'),
    ],
    7: [  # корпусы
        ('brand', 'Производитель'),
        ('form_factor', 'Типоразмер'),
        ('mb_support', 'Макс. форм-фактор платы'),
        ('window', 'Боковое окно'),
        ('fans_count', 'Вентиляторов в комплекте'),
        ('rgb', 'Подсветка'),
        ('color', 'Цвет'),
    ],
    8: [  # блоки питания
        ('brand', 'Производитель'),
        ('power', 'Мощность, Вт'),
        ('certificate', 'Сертификат'),
        ('modular', 'Модульные кабели'),
        ('connector_12v', 'Разъём 12V-2x6 для видеокарт'),
        ('form_factor', 'Форм-фактор'),
        ('color', 'Цвет'),
    ],
    9: [  # вентиляторы
        ('brand', 'Производитель'),
        ('fan_size', 'Размер, мм'),
        ('connector', 'Разъём'),
        ('pack_count', 'Штук в комплекте'),
        ('bearing', 'Тип подшипника'),
        ('rgb', 'Подсветка'),
        ('color', 'Цвет'),
    ],
}


# значение из <select name="sort"> → (подпись, порядок для order_by)
SORTS = {
    '': ('По умолчанию', ['id']),
    'price': ('Сначала дешёвые', ['price', 'id']),
    'price_desc': ('Сначала дорогие', ['-price', 'id']),
    'name': ('По названию', ['name']),
}


def build_filters(request, products, fields):
    """Собирает список фильтров для шаблона."""
    filters = []
    for name, title in fields:
        values = products.values_list(name, flat=True).distinct().order_by(name)
        filters.append({
            'name': name,
            'title': title,
            'values': [str(v) for v in values if v not in ('', None)],
            'selected': request.GET.getlist(name),
        })
    return filters


def apply_filters(request, products, fields):
    """Оставляет только товары, подходящие под отмеченные галочки, цену и наличие."""
    for name, _ in fields:
        selected = request.GET.getlist(name)
        if selected:
            products = products.filter(**{f'{name}__in': selected})

    # isdigit — чтобы адрес вроде ?price_min=abc не ронял страницу
    price_min = request.GET.get('price_min', '')
    price_max = request.GET.get('price_max', '')
    if price_min.isdigit():
        products = products.filter(price__gte=price_min)
    if price_max.isdigit():
        products = products.filter(price__lte=price_max)

    if request.GET.get('in_stock'):
        products = products.filter(quantity__gt=0)

    return products


def get_products_with_basket(request, products, page_number):
    paginator = Paginator(products, PRODUCTS_PER_PAGE)
    page = paginator.get_page(page_number)
    page.object_list = list(page.object_list)

    config_product_ids = get_config_product_ids(request)
    for product in page.object_list:
        product.in_config = product.id in config_product_ids

    if request.user.is_authenticated:
        baskets = Basket.objects.filter(user=request.user)
        basket_by_product = {basket.product_id: basket for basket in baskets}
        favorite_ids = set(Favorite.objects.filter(user=request.user).values_list('product_id', flat=True))
        for product in page.object_list:
            product.basket = basket_by_product.get(product.id)
            product.is_favorite = product.id in favorite_ids

    return page

def products(request, category_id=None, page_number=1):
    if category_id:
        category = get_object_or_404(ProductCategory, id=category_id)
        products = Product.objects.filter(category_id=category_id)
        category_title = category.name
    else:
        products = Product.objects.all()
        category_title = 'Все товары'

    fields = CATEGORY_FILTERS.get(category_id, [])
    filtered = apply_filters(request, products, fields)

    # в order_by идёт только значение из SORTS: неизвестный ?sort=... даёт порядок по умолчанию
    sort = request.GET.get('sort', '')
    if sort not in SORTS:
        sort = ''
    filtered = filtered.order_by(*SORTS[sort][1])

    context = {
        'title': 'Каталог',
        'category_title': category_title,
        'category_id': category_id,
        'products': get_products_with_basket(request, filtered, page_number),
        'categories': ProductCategory.objects.all(),
        'filters': build_filters(request, products, fields),
        'price_range': products.aggregate(min=Min('price'), max=Max('price')),
        # топ-5 раздела по количеству проданных штук (из истории заказов), фильтры на него не влияют
        'top_products': products.annotate(sold=Sum('order_items__quantity'))
                                .filter(sold__gt=0).order_by('-sold', 'id')[:5],
        'sorts': [(value, label) for value, (label, _) in SORTS.items()],
        'current_sort': sort,
    }
    return render(request, "products/base_catalog.html", context)


def product_detail(request, product_id):
    product = get_object_or_404(Product.objects.select_related('category'), id=product_id)

    # характеристики — те же поля, что в фильтрах категории, только заполненные
    specs = []
    for name, title in CATEGORY_FILTERS.get(product.category_id, []):
        value = getattr(product, name)
        if value not in ('', None):
            specs.append((title, value))

    basket = None
    is_favorite = False
    if request.user.is_authenticated:
        basket = Basket.objects.filter(user=request.user, product=product).first()
        is_favorite = Favorite.objects.filter(user=request.user, product=product).exists()

    context = {
        'title': product.name,
        'product': product,
        'specs': specs,
        'basket': basket,
        'is_favorite': is_favorite,
        'in_config': product.id in get_config_product_ids(request),
        'sold': product.order_items.aggregate(total=Sum('quantity'))['total'] or 0,
        'similar': Product.objects.filter(category=product.category).exclude(id=product.id).order_by('price')[:4],
    }
    return render(request, "products/product.html", context)


def index(request):
    context = {
        'title': 'ONLINE STORE',
    }
    return render(request, "products/index.html", context)

# Строки конфигуратора: ключ строки → id категории (id из админки)
CONFIG_SLOTS = {
    'cpu': 2,           # процессоры
    'motherboard': 3,   # материнские платы
    'ram': 4,           # оперативная память
    'gpu': 1,           # видеокарты
    'storage': 5,       # хранение данных
    'cooling': 6,       # охлаждение процессора
    'case': 7,          # корпусы
    'psu': 8,           # блоки питания
    'fans': 9,          # вентиляторы
}
CONFIG_REQUIRED = ['cpu', 'motherboard', 'ram', 'storage', 'cooling', 'case', 'psu']
# строки, куда можно добавить несколько разных товаров (в ПК часто ставят несколько накопителей и вентиляторов)
CONFIG_MULTI = ['storage', 'fans']
MULTI_CATEGORY_IDS = [CONFIG_SLOTS[key] for key in CONFIG_MULTI]


def get_config(request):
    """Сборка хранится в сессии: {id категории (строкой): [id товаров]}. Работает и без входа в аккаунт.
    В обычной строке в списке максимум один товар, в строках из CONFIG_MULTI — сколько угодно."""
    config = request.session.get('config', {})
    # раньше хранился один id, а не список — переводим старые сессии в новый вид
    return {category: ids if isinstance(ids, list) else [ids] for category, ids in config.items()}


def get_config_product_ids(request):
    """Все id товаров сборки одним множеством — для пометок «В конфигураторе ✓»."""
    return {product_id for ids in get_config(request).values() for product_id in ids}


def config(request):
    chosen = get_config(request)
    chosen_products = Product.objects.in_bulk(get_config_product_ids(request))

    slots = {}
    for key, category_id in CONFIG_SLOTS.items():
        products = [chosen_products[i] for i in chosen.get(str(category_id), []) if i in chosen_products]
        slots[key] = {
            'category_id': category_id,
            'multi': key in CONFIG_MULTI,
            'products': products,
            'product': products[0] if products else None,
        }
    selected = [product for slot in slots.values() for product in slot['products']]

    context = {
        'title': 'Конфигуратор',
        'slots': slots,
        'selected_count': sum(1 for slot in slots.values() if slot['products']),
        'slots_count': len(CONFIG_SLOTS),
        'required_done': sum(1 for key in CONFIG_REQUIRED if slots[key]['products']),
        'required_count': len(CONFIG_REQUIRED),
        'total': sum(product.price for product in selected),
    }
    return render(request, "products/configurator.html", context)


@require_POST
def config_add(request, product_id):
    """Кнопка «В конфигуратор» в каталоге: товар встаёт в строку своей категории.
    В обычной строке прежний товар заменяется, в строке из CONFIG_MULTI — добавляется к остальным."""
    product = get_object_or_404(Product, id=product_id)
    if product.category_id in CONFIG_SLOTS.values():
        config = get_config(request)
        key = str(product.category_id)
        if product.category_id in MULTI_CATEGORY_IDS:
            if product.id not in config.get(key, []):
                config[key] = config.get(key, []) + [product.id]
        else:
            config[key] = [product.id]
        request.session['config'] = config
    return redirect('config')


@login_required(login_url='users:login')
@require_POST
def config_to_basket(request):
    """Кнопка «Добавить в корзину» в конфигураторе: вся сборка по 1 шт. каждого товара.
    Если товар уже лежит в корзине, его количество увеличивается на 1, как у кнопки «+»."""
    products = Product.objects.filter(id__in=get_config_product_ids(request))
    for product in products:
        basket, created = Basket.objects.get_or_create(user=request.user, product=product)
        if not created:
            basket.quantity += 1
            basket.save()
    return redirect('users:basket')


@require_POST
def config_remove(request, product_id):
    """Крестик в конфигураторе: убрать товар из сборки (в строке с несколькими товарами — только этот)."""
    config = get_config(request)
    for category, ids in config.items():
        config[category] = [i for i in ids if i != product_id]
    request.session['config'] = {category: ids for category, ids in config.items() if ids}
    return redirect('config')



