from django.contrib import admin

# Register your models here.

from users.models import Profile, Basket, Favorite, Order, OrderItem


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'created')
    search_fields = ('user__username', 'product__name')


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone')
    search_fields = ('user__username', 'phone')


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'created', 'status')
    list_filter = ('user', 'status')
    # поиск по имени пользователя: user__username — переход по связи к полю username модели User
    search_fields = ('user__username',)
    inlines = [OrderItemInline]


@admin.register(Basket)
class BasketAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'quantity')
    search_fields = ('user__username', 'product__name')
    ordering = ('user__username',)