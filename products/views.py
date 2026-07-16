from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.


def index(request):
    return render(request, "products/index.html")

def config(request):
    return render(request, "products/configurator.html")