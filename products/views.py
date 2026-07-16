from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.


def index(request):
    return render(request, "products/index.html")

def check(request):
    return render(request, "products/config_test.html")