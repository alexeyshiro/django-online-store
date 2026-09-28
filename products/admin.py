from django.contrib import admin

# Register your models here.


from products.models import Product, ProductCategory


@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "quantity",)
    list_filter = ("category",)
    search_fields = ("name",)
    ordering = ("name",)

