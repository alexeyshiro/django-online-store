from django.http import HttpResponse
from django.shortcuts import render
from django.template.defaultfilters import title
from products.models import Product, ProductCategory

# Create your views here.


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
        'products': Product.objects.all(),
        'categories': ProductCategory.objects.all(),
        'filters_template': 'products/includes/filters_motherboard.html',
    }
    return render(request, "products/base_catalog.html", context)

def cpu(request):
    context = {
        'title': 'Каталог',
        'category_title': 'Процессоры',
        'products': Product.objects.all(),
        'categories': ProductCategory.objects.all(),
        'filters_template': 'products/includes/filters_cpu.html',
    }
    return render(request, "products/base_catalog.html", context)

def gpu(request):
    context = {
        'title': 'Каталог',
        'category_title': 'Видеокарты',
        'products': Product.objects.all(),
        'categories': ProductCategory.objects.all(),
        'filters_template': 'products/includes/filters_gpu.html',
    }
    return render(request, "products/base_catalog.html", context)