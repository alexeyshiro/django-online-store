from django.urls import path
from users.views import login_view, register_view, logout_view, account_view, history_view, favorites_view


app_name = "users"


urlpatterns = [
    path('login/', login_view, name='login'),
    path('register/', register_view, name='register'),
    path('logout/', logout_view, name='logout'),
    path('account/', account_view, name='account'),
    path('history/', history_view, name='history'),
    path('favorites/', favorites_view, name='favorites'),
]
