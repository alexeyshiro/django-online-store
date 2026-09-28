from django.db import models

# Create your models here.


class ProductCategory(models.Model):
    name = models.CharField(max_length=64, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=128, unique=True)
    image = models.ImageField(upload_to="products_media", blank=True)
    description = models.TextField(blank=True)
    short_description = models.TextField(max_length=128, blank=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    quantity = models.PositiveIntegerField(default=0)
    category = models.ForeignKey(ProductCategory, on_delete=models.CASCADE)

    # Характеристики для фильтров. У каждой категории заполнены только свои поля,
    # какие поля у какой категории — см. CATEGORY_FILTERS в products/views.py.

    # общие для многих категорий
    brand = models.CharField(max_length=64, blank=True)                 # производитель
    color = models.CharField(max_length=32, blank=True)                 # цвет
    rgb = models.CharField(max_length=8, blank=True)                    # подсветка: Есть / Нет
    series = models.CharField(max_length=32, blank=True)                # серия: GeForce RTX 40, Ryzen 7
    memory = models.PositiveIntegerField(null=True, blank=True)         # объём памяти, ГБ (видеокарты, ОЗУ)
    memory_type = models.CharField(max_length=16, blank=True)           # GDDR6, DDR5
    socket = models.CharField(max_length=32, blank=True)                # AM5, LGA1700
    tdp = models.PositiveIntegerField(null=True, blank=True)            # тепловыделение / рассеиваемая мощность, Вт
    form_factor = models.CharField(max_length=32, blank=True)           # ATX, Micro-ATX, DIMM, M.2 2280, Mid-Tower
    fan_size = models.PositiveIntegerField(null=True, blank=True)       # размер вентилятора, мм

    # видеокарты
    chip_vendor = models.CharField(max_length=16, blank=True)           # NVIDIA, AMD, Intel
    bus_width = models.PositiveIntegerField(null=True, blank=True)      # разрядность шины, бит
    pcie = models.CharField(max_length=8, blank=True)                   # версия PCI Express: 4.0, 5.0

    # процессоры
    cores = models.PositiveIntegerField(null=True, blank=True)
    threads = models.PositiveIntegerField(null=True, blank=True)
    integrated_graphics = models.CharField(max_length=8, blank=True)    # Есть / Нет
    package = models.CharField(max_length=8, blank=True)                # BOX / OEM

    # материнские платы
    chipset = models.CharField(max_length=16, blank=True)               # B650, B760
    memory_slots = models.PositiveIntegerField(null=True, blank=True)
    wifi = models.CharField(max_length=8, blank=True)                   # Есть / Нет

    # оперативная память
    modules = models.PositiveIntegerField(null=True, blank=True)        # модулей в комплекте
    frequency = models.PositiveIntegerField(null=True, blank=True)      # частота, МГц
    latency = models.PositiveIntegerField(null=True, blank=True)        # CL

    # хранение данных
    drive_type = models.CharField(max_length=16, blank=True)            # SSD M.2, SSD 2.5", HDD
    capacity = models.PositiveIntegerField(null=True, blank=True)       # объём, ГБ
    interface = models.CharField(max_length=32, blank=True)             # PCIe 4.0 x4, SATA III

    # охлаждение процессора
    cooling_type = models.CharField(max_length=32, blank=True)          # Башенный, Жидкостное (СЖО)

    # корпусы
    mb_support = models.CharField(max_length=16, blank=True)            # макс. форм-фактор платы
    window = models.CharField(max_length=8, blank=True)                 # боковое окно: Есть / Нет
    fans_count = models.PositiveIntegerField(null=True, blank=True)     # вентиляторов в комплекте

    # блоки питания
    power = models.PositiveIntegerField(null=True, blank=True)          # мощность, Вт
    certificate = models.CharField(max_length=32, blank=True)           # 80 PLUS Bronze / Gold
    modular = models.CharField(max_length=16, blank=True)               # модульность: Нет / Частично / Полностью
    connector_12v = models.CharField(max_length=8, blank=True)          # разъём 12V-2x6 для видеокарт: Есть / Нет

    # вентиляторы
    connector = models.CharField(max_length=16, blank=True)             # 3-pin, 4-pin PWM
    pack_count = models.PositiveIntegerField(null=True, blank=True)     # штук в комплекте
    bearing = models.CharField(max_length=32, blank=True)               # тип подшипника

    def __str__(self):
        return f"{self.name} | {self.category.name}"