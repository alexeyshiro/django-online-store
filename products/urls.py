from django.urls import path
from products.views import motherboards, cpu, gpu


app_name = "products"


urlpatterns = [
    path('motherboards/', motherboards, name='motherboards'),
    path('cpu/', cpu, name='cpu'),
    path('gpu/', gpu, name='gpu'),
]