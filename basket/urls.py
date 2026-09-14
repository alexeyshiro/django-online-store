from django.urls import path
from basket.views import basket_view


app_name = "basket"


urlpatterns = [
    path('', basket_view, name='basket'),
]
