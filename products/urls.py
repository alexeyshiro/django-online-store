from django.urls import path
from products.views import products, product_detail


app_name = "products"


urlpatterns = [
    path('', products, name='index'),
    path('category/<int:category_id>/', products, name="category"),
    path('page/<int:page_number>/', products, name="page"),
    path('category/<int:category_id>/page/<int:page_number>/', products, name="category_page"),
    path('product/<int:product_id>/', product_detail, name='product'),
]