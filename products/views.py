from django.http import HttpResponse
from django.shortcuts import render
from django.template.defaultfilters import title
from products.models import Product, ProductCategory

# Create your views here.


def index(request):
    context = {
        "title": "ONLINE STORE",
    }
    return render(request, "products/index.html", context)

def config(request):
    context = {
        "title": "Конфигуратор",
        'products': Product.objects.all(),
        'categories': ProductCategory.objects.all(),
    }
    # print(context["products"])
    # print(context["categories"])

    return render(request, "products/configurator.html", context)

def catalog_motherboards(request):
    context = {
        "title": "Каталог",
        'products': Product.objects.all(),
        'categories': ProductCategory.objects.all(),
    }
    return render(request, "products/catalog_motherboards.html", context)