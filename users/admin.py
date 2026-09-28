from django.contrib import admin

# Register your models here.

from users.models import Profile, Basket, Favorite, Order, OrderItem


admin.site.register(Profile)
admin.site.register(Basket)
admin.site.register(Favorite)


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'created', 'status')
    list_filter = ('user', 'status')
    inlines = [OrderItemInline]
