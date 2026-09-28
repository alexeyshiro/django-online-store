"""
Создаёт категории с главной страницы и по несколько тестовых товаров в каждой,
чтобы было на чём проверять фильтры.

Запуск:  python manage.py seed_catalog

Команду можно запускать повторно: категории и товары ищутся по названию
и обновляются, а не создаются второй раз.
"""
from django.core.management.base import BaseCommand
from django.db import transaction

from products.models import Product, ProductCategory


# Категории в том порядке, в каком они на главной.
# Второе значение — старые названия, которые нужно переименовать.
CATEGORIES = [
    ('Видеокарты', ['видеокарты']),
    ('Процессоры', ['проц']),
    ('Материнские платы', []),
    ('Оперативная память', []),
    ('Хранение данных', []),
    ('Охлаждение процессора', []),
    ('Корпусы', []),
    ('Блоки питания', []),
    ('Вентиляторы', []),
]

PRODUCTS = {
    'Видеокарты': [
        dict(name='Palit GeForce RTX 4060 Dual 8 ГБ', price=32999, quantity=7,
             brand='Palit', chip_vendor='NVIDIA', series='GeForce RTX 40', memory=8, memory_type='GDDR6',
             bus_width=128, pcie='4.0', color='Чёрный', rgb='Нет'),
        dict(name='Sapphire Radeon RX 9070 XT Pulse 16 ГБ', price=74999, quantity=3,
             brand='Sapphire', chip_vendor='AMD', series='Radeon RX 9000', memory=16, memory_type='GDDR6',
             bus_width=256, pcie='5.0', color='Чёрный', rgb='Нет'),
        dict(name='ASUS Dual GeForce RTX 5060 Ti White 16 ГБ', price=52999, quantity=0,
             brand='ASUS', chip_vendor='NVIDIA', series='GeForce RTX 50', memory=16, memory_type='GDDR7',
             bus_width=128, pcie='5.0', color='Белый', rgb='Есть'),
    ],
    'Процессоры': [
        dict(name='AMD Ryzen 5 7600 OEM', price=17999, quantity=12,
             brand='AMD', series='Ryzen 5', socket='AM5', cores=6, threads=12,
             integrated_graphics='Есть', tdp=65, package='OEM', memory_type='DDR5'),
        dict(name='Intel Core i5-14600KF BOX', price=24999, quantity=5,
             brand='Intel', series='Core i5', socket='LGA1700', cores=14, threads=20,
             integrated_graphics='Нет', tdp=125, package='BOX', memory_type='DDR5'),
        dict(name='AMD Ryzen 7 9800X3D BOX', price=54999, quantity=2,
             brand='AMD', series='Ryzen 7', socket='AM5', cores=8, threads=16,
             integrated_graphics='Есть', tdp=120, package='BOX', memory_type='DDR5'),
    ],
    'Материнские платы': [
        dict(name='MSI MAG B650 TOMAHAWK WIFI', price=21999, quantity=4,
             brand='MSI', socket='AM5', chipset='B650', form_factor='ATX', memory_type='DDR5',
             memory_slots=4, wifi='Есть', color='Чёрный'),
        dict(name='ASUS PRIME B760M-A D4', price=11999, quantity=6,
             brand='ASUS', socket='LGA1700', chipset='B760', form_factor='Micro-ATX', memory_type='DDR4',
             memory_slots=4, wifi='Нет', color='Чёрный'),
        dict(name='GIGABYTE A520M K V2', price=5999, quantity=0,
             brand='GIGABYTE', socket='AM4', chipset='A520', form_factor='Micro-ATX', memory_type='DDR4',
             memory_slots=2, wifi='Нет', color='Чёрный'),
    ],
    'Оперативная память': [
        dict(name='Kingston FURY Beast 32 ГБ (2x16 ГБ) DDR5-6000', price=11499, quantity=10,
             brand='Kingston', memory_type='DDR5', memory=32, modules=2, frequency=6000, latency=36,
             form_factor='DIMM', rgb='Нет', color='Чёрный'),
        dict(name='G.Skill Trident Z5 RGB 64 ГБ (2x32 ГБ) DDR5-6400', price=24999, quantity=2,
             brand='G.Skill', memory_type='DDR5', memory=64, modules=2, frequency=6400, latency=32,
             form_factor='DIMM', rgb='Есть', color='Серебристый'),
        dict(name='Crucial 16 ГБ DDR4-3200 SO-DIMM', price=3499, quantity=0,
             brand='Crucial', memory_type='DDR4', memory=16, modules=1, frequency=3200, latency=22,
             form_factor='SO-DIMM', rgb='Нет', color='Зелёный'),
    ],
    'Хранение данных': [
        dict(name='Samsung 990 PRO 1 ТБ', price=12999, quantity=8,
             brand='Samsung', drive_type='SSD M.2', capacity=1000, interface='PCIe 4.0 x4',
             form_factor='M.2 2280'),
        dict(name='Kingston A400 480 ГБ', price=3299, quantity=15,
             brand='Kingston', drive_type='SSD 2.5"', capacity=480, interface='SATA III',
             form_factor='2.5"'),
        dict(name='WD Blue 2 ТБ', price=6499, quantity=0,
             brand='WD', drive_type='HDD', capacity=2000, interface='SATA III',
             form_factor='3.5"'),
    ],
    'Охлаждение процессора': [
        dict(name='DeepCool AK400', price=2799, quantity=9,
             brand='DeepCool', cooling_type='Башенный', tdp=220, fan_size=120, rgb='Нет', color='Чёрный'),
        dict(name='ID-COOLING SE-224-XTS ARGB White', price=2499, quantity=4,
             brand='ID-COOLING', cooling_type='Башенный', tdp=220, fan_size=120, rgb='Есть', color='Белый'),
        dict(name='ARCTIC Liquid Freezer III 360', price=10999, quantity=1,
             brand='ARCTIC', cooling_type='Жидкостное (СЖО)', tdp=300, fan_size=120, rgb='Нет', color='Чёрный'),
    ],
    'Корпусы': [
        dict(name='DeepCool CH560 Digital', price=8499, quantity=3,
             brand='DeepCool', form_factor='Mid-Tower', mb_support='E-ATX', window='Есть', fans_count=4,
             rgb='Есть', color='Чёрный'),
        dict(name='Cooler Master MasterBox Q300L', price=4299, quantity=5,
             brand='Cooler Master', form_factor='Mini-Tower', mb_support='Micro-ATX', window='Есть', fans_count=1,
             rgb='Нет', color='Чёрный'),
        dict(name='Lian Li O11 Dynamic EVO White', price=15999, quantity=0,
             brand='Lian Li', form_factor='Mid-Tower', mb_support='E-ATX', window='Есть', fans_count=0,
             rgb='Нет', color='Белый'),
    ],
    'Блоки питания': [
        dict(name='DeepCool PK650D 650 Вт', price=5299, quantity=11,
             brand='DeepCool', power=650, certificate='80 PLUS Bronze', modular='Нет', form_factor='ATX',
             connector_12v='Нет', color='Чёрный'),
        dict(name='be quiet! Pure Power 12 M 850 Вт', price=12999, quantity=3,
             brand='be quiet!', power=850, certificate='80 PLUS Gold', modular='Полностью', form_factor='ATX',
             connector_12v='Есть', color='Чёрный'),
        dict(name='Chieftec Polaris 3.0 1050 Вт', price=14999, quantity=0,
             brand='Chieftec', power=1050, certificate='80 PLUS Gold', modular='Частично', form_factor='ATX',
             connector_12v='Есть', color='Чёрный'),
    ],
    'Вентиляторы': [
        dict(name='ARCTIC P12 PWM PST', price=599, quantity=30,
             brand='ARCTIC', fan_size=120, connector='4-pin PWM', pack_count=1, bearing='Гидродинамический',
             rgb='Нет', color='Чёрный'),
        dict(name='DeepCool FC120 3 in 1', price=2999, quantity=6,
             brand='DeepCool', fan_size=120, connector='4-pin PWM', pack_count=3, bearing='Гидродинамический',
             rgb='Есть', color='Чёрный'),
        dict(name='be quiet! Pure Wings 3 140 мм', price=899, quantity=0,
             brand='be quiet!', fan_size=140, connector='3-pin', pack_count=1, bearing='Скольжения',
             rgb='Нет', color='Чёрный'),
    ],
}


class Command(BaseCommand):
    help = 'Создаёт категории с главной страницы и тестовые товары для проверки фильтров'

    @transaction.atomic
    def handle(self, *args, **options):
        categories = {}
        for name, old_names in CATEGORIES:
            ProductCategory.objects.filter(name__in=old_names).update(name=name)
            category, created = ProductCategory.objects.get_or_create(name=name)
            categories[name] = category
            self.stdout.write(f'{category.id:>3}  {name}' + ('  (создана)' if created else ''))

        for category_name, items in PRODUCTS.items():
            for item in items:
                item = dict(item)
                name = item.pop('name')
                Product.objects.update_or_create(
                    name=name,
                    defaults={**item, 'category': categories[category_name]},
                )

        self.stdout.write(self.style.SUCCESS(f'Готово, товаров в базе: {Product.objects.count()}'))
