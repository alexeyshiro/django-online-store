"""
Создаёт тестовую историю покупок пользователям admin и lol66222,
чтобы проверить страницу «История покупок» и блок «Топ-5 по продажам».

Запуск:  python manage.py seed_orders
(сначала должны быть товары: python manage.py seed_catalog)

Команду можно запускать повторно: заказы этих двух пользователей
удаляются и создаются заново, дубликатов не будет.
"""
from datetime import timedelta

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from products.models import Product
from users.models import Order, OrderItem


# пользователь → список заказов: (сколько дней назад, [(название товара, количество), ...])
ORDERS = {
    'admin': [
        (120, [('AMD Ryzen 5 7600 OEM', 1), ('MSI MAG B650 TOMAHAWK WIFI', 1),
               ('Kingston FURY Beast 32 ГБ (2x16 ГБ) DDR5-6000', 1), ('Samsung 990 PRO 1 ТБ', 1),
               ('DeepCool AK400', 1), ('DeepCool CH560 Digital', 1), ('DeepCool PK650D 650 Вт', 1),
               ('Palit GeForce RTX 4060 Dual 8 ГБ', 1)]),
        (90, [('ARCTIC P12 PWM PST', 3), ('Samsung 990 PRO 1 ТБ', 1)]),
        (60, [('ASUS Dual GeForce RTX 5060 Ti White 16 ГБ', 1), ('be quiet! Pure Power 12 M 850 Вт', 1)]),
        (30, [('Palit GeForce RTX 4060 Dual 8 ГБ', 1), ('Kingston A400 480 ГБ', 2)]),
        (7, [('ARCTIC P12 PWM PST', 2), ('ID-COOLING SE-224-XTS ARGB White', 1),
             ('G.Skill Trident Z5 RGB 64 ГБ (2x32 ГБ) DDR5-6400', 1)]),
    ],
    'lol66222': [
        (100, [('Intel Core i5-14600KF BOX', 1), ('ASUS PRIME B760M-A D4', 1), ('Crucial 16 ГБ DDR4-3200 SO-DIMM', 2),
               ('WD Blue 2 ТБ', 1), ('ARCTIC Liquid Freezer III 360', 1), ('Cooler Master MasterBox Q300L', 1),
               ('DeepCool PK650D 650 Вт', 1), ('ASUS Dual GeForce RTX 5060 Ti White 16 ГБ', 1)]),
        (75, [('AMD Ryzen 5 7600 OEM', 1), ('MSI MAG B650 TOMAHAWK WIFI', 1),
              ('Kingston FURY Beast 32 ГБ (2x16 ГБ) DDR5-6000', 2)]),
        (45, [('Palit GeForce RTX 4060 Dual 8 ГБ', 2), ('DeepCool FC120 3 in 1', 1)]),
        (20, [('Samsung 990 PRO 1 ТБ', 1), ('Sapphire Radeon RX 9070 XT Pulse 16 ГБ', 1), ('DeepCool AK400', 1)]),
        (3, [('ARCTIC P12 PWM PST', 4), ('Sapphire Radeon RX 9070 XT Pulse 16 ГБ', 1), ('AMD Ryzen 7 9800X3D BOX', 1)]),
    ],
}


class Command(BaseCommand):
    help = 'Создаёт тестовую историю покупок пользователям admin и lol66222'

    @transaction.atomic
    def handle(self, *args, **options):
        products = {p.name: p for p in Product.objects.all()}
        now = timezone.now()

        for username, orders in ORDERS.items():
            user = User.objects.filter(username=username).first()
            if not user:
                self.stdout.write(self.style.WARNING(f'Пользователь {username} не найден, пропускаю'))
                continue

            Order.objects.filter(user=user).delete()
            for days_ago, items in orders:
                order = Order.objects.create(user=user, created=now - timedelta(days=days_ago))
                for name, quantity in items:
                    if name not in products:
                        raise CommandError(f'Нет товара «{name}». Сначала запустите: python manage.py seed_catalog')
                    product = products[name]
                    OrderItem.objects.create(order=order, product=product, quantity=quantity, price=product.price)

            self.stdout.write(f'{username}: заказов {len(orders)}')

        self.stdout.write(self.style.SUCCESS('Готово'))
