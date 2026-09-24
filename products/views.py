from django.core.paginator import Paginator
from django.shortcuts import render
from products.models import Product, ProductCategory
from users.models import Basket

# Create your views here.

PRODUCTS_PER_PAGE = 12


def get_products_with_basket(request):
    paginator = Paginator(Product.objects.order_by('id'), PRODUCTS_PER_PAGE)
    page = paginator.get_page(request.GET.get('page'))
    page.object_list = list(page.object_list)

    if request.user.is_authenticated:
        baskets = Basket.objects.filter(user=request.user)
        basket_by_product = {basket.product_id: basket for basket in baskets}
        for product in page.object_list:
            product.basket = basket_by_product.get(product.id)

    return page


def index(request):
    context = {
        'title': 'ONLINE STORE',
    }
    return render(request, "products/index.html", context)

def config(request):
    context = {
        'title': 'Конфигуратор',
        'products': Product.objects.all(),
        'categories': ProductCategory.objects.all(),
    }
    # print(context["products"])
    # print(context["categories"])

    return render(request, "products/configurator.html", context)


def motherboards(request):
    context = {
        'title': 'Каталог',
        'category_title': 'Материнские платы',
        'products': get_products_with_basket(request),
        'categories': ProductCategory.objects.all(),
        'filters_template': 'products/includes/filters_motherboard.html',
    }
    return render(request, "products/base_catalog.html", context)

def cpu(request):
    context = {
        'title': 'Каталог',
        'category_title': 'Процессоры',
        'products': get_products_with_basket(request),
        'categories': ProductCategory.objects.all(),
        'filters_template': 'products/includes/filters_cpu.html',
    }
    return render(request, "products/base_catalog.html", context)

def gpu(request):
    context = {
        'title': 'Каталог',
        'category_title': 'Видеокарты',
        'products': get_products_with_basket(request),
        'categories': ProductCategory.objects.all(),
        'filters_template': 'products/includes/filters_gpu.html',
    }
    return render(request, "products/base_catalog.html", context)
