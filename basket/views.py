from django.shortcuts import render

# Create your views here.


def basket_view(request):
    context = {
        'title': 'Корзина',
    }
    return render(request, "basket/basket.html", context)
