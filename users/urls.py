from django.urls import path
from users.views import login_view, register_view, logout_view, account_view, history_view, favorites_view, basket_view
from users.views import basket_add, basket_decrease, basket_remove


app_name = "users"


urlpatterns = [
    path('login/', login_view, name='login'),
    path('register/', register_view, name='register'),
    path('logout/', logout_view, name='logout'),
    path('account/', account_view, name='account'),
    path('history/', history_view, name='history'),
    path('favorites/', favorites_view, name='favorites'),
    path('basket/', basket_view, name='basket'),
    path('basket/add/<int:product_id>/', basket_add, name='basket_add'),
    path('basket/decrease/<int:basket_id>/', basket_decrease, name='basket_decrease'),
    path('basket/remove/<int:basket_id>/', basket_remove, name='basket_remove'),
]
