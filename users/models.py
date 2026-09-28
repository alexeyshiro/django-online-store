from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone

from products.models import Product

# Create your models here.


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return f"Профиль {self.user.username}"


class Basket(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='baskets')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveSmallIntegerField(default=1)

    def __str__(self):
        return f"Корзина {self.user.username} | {self.product.name}"

    def sum(self):
        return self.product.price * self.quantity


class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        # один и тот же товар не может попасть в избранное дважды
        unique_together = ('user', 'product')

    def __str__(self):
        return f"Избранное {self.user.username} | {self.product.name}"


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    created = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=32, default='Выполнен')

    class Meta:
        ordering = ['-created']

    def __str__(self):
        return f"Заказ №{self.id} | {self.user.username}"

    def total(self):
        return sum(item.sum() for item in self.items.all())


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    # related_name нужен для подсчёта продаж: Product.objects.annotate(sold=Sum('order_items__quantity'))
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='order_items')
    quantity = models.PositiveSmallIntegerField(default=1)
    # цена на момент покупки: если потом цену товара поменяют, в истории останется старая
    price = models.DecimalField(max_digits=8, decimal_places=2)

    def __str__(self):
        return f"{self.product.name} × {self.quantity}"

    def sum(self):
        return self.price * self.quantity
