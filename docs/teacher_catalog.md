# Каталог по способу преподавателя: категории через id и фильтры

Делается в две части, строго по порядку:

1. **Выбор категории.** Один view `products`, категория приходит в адресе как число: `/products/category/1/`.
2. **Фильтрация по характеристикам.** Характеристики — поля в `Product`, фильтры приходят GET-запросом, галочки рисует один общий шаблон.

---

# Часть 1. Выбор категории через id

## Как это работает

**категория лежит в базе → ссылка в шаблоне кладёт её id в адрес → `urls.py` достаёт id из адреса → view по нему отбирает товары.**

`id` Django проставляет каждой категории сам, в модель ничего добавлять не нужно. Посмотреть id можно в админке: он виден в адресе при открытии категории (`/admin/products/productcategory/1/change/`).

| id | name |
|----|------|
| 1  | Видеокарты |
| 2  | Процессоры |
| …  | … |

> Проверь в админке, какой id у какой категории на самом деле. Дальше эти числа понадобятся в ссылках на главной странице и в словаре фильтров.

## Шаг 1. Маршруты — `products/urls.py`

Эти строки у тебя уже есть закомментированными. Заменяем ими маршруты `motherboards/`, `cpu/`, `gpu/`:

```python
from django.urls import path
from products.views import products

app_name = "products"

urlpatterns = [
    path('', products, name='index'),
    path('category/<int:category_id>/', products, name='category'),
    path('page/<int:page_number>/', products, name='page'),
    path('category/<int:category_id>/page/<int:page_number>/', products, name='category_page'),
]
```

Все четыре маршрута ведут в **один** view. Разница только в том, что приходит из адреса:

| Адрес | Что получит view |
|---|---|
| `/products/` | ничего → все товары, страница 1 |
| `/products/category/1/` | `category_id=1` → страница 1 |
| `/products/page/2/` | `page_number=2` → все товары |
| `/products/category/1/page/2/` | `category_id=1`, `page_number=2` |

`<int:...>` значит «в этом месте адреса число, передай его во view под этим именем».

Строку `from itertools import product` вверху файла можно удалить, она не используется.

## Шаг 2. View — `products/views.py`

Функцию `get_products_with_basket` меняем так, чтобы она получала уже отобранные товары и номер страницы:

```python
def get_products_with_basket(request, products, page_number):
    paginator = Paginator(products.order_by('id'), PRODUCTS_PER_PAGE)
    page = paginator.get_page(page_number)
    page.object_list = list(page.object_list)

    if request.user.is_authenticated:
        baskets = Basket.objects.filter(user=request.user)
        basket_by_product = {basket.product_id: basket for basket in baskets}
        for product in page.object_list:
            product.basket = basket_by_product.get(product.id)

    return page
```

Вместо `motherboards`, `cpu`, `gpu` пишем один view:

```python
from django.shortcuts import render, get_object_or_404


def products(request, category_id=None, page_number=1):
    if category_id:
        category = get_object_or_404(ProductCategory, id=category_id)
        products = Product.objects.filter(category_id=category_id)
        category_title = category.name
    else:
        products = Product.objects.all()
        category_title = 'Все товары'

    context = {
        'title': 'Каталог',
        'category_title': category_title,
        'category_id': category_id,
        'products': get_products_with_basket(request, products, page_number),
        'categories': ProductCategory.objects.all(),
    }
    return render(request, "products/base_catalog.html", context)
```

Пояснения:

- `category_id=None` и `page_number=1` — значения по умолчанию. Если в адресе их нет (`/products/`), view всё равно работает.
- `filter(category_id=category_id)` стоит **до** пагинатора, поэтому страницы и счётчик товаров считаются только по этой категории.
- `get_object_or_404`: если в адресе id несуществующей категории (`/category/99/`), будет страница 404, а не ошибка сервера.
- `category_id` передаётся в шаблон, чтобы подсветить активную вкладку и строить ссылки на страницы.
- Внутри функции `products` переменная тоже называется `products` — так в примере преподавателя, Python это допускает (внутри функции имя означает переменную).

## Шаг 3. Временно убрать старые фильтры — `base_catalog.html`

Сейчас в шаблоне стоит `{% include filters_template %}`, а view больше не передаёт `filters_template`. Пустой include даст ошибку, поэтому эту строку пока удаляем. Фильтры вернутся в части 2.

## Шаг 4. Вкладки категорий — `base_catalog.html`

```django
<nav class="category-switch">
  <a href="{% url 'products:index' %}"
     class="cat-tab {% if not category_id %}active{% endif %}">Все товары</a>

  {% for category in categories %}
    <a href="{% url 'products:category' category.id %}"
       class="cat-tab {% if category.id == category_id %}active{% endif %}">
      {{ category.name }}
    </a>
  {% endfor %}
</nav>
```

`{% url 'products:category' category.id %}` подставляет id в маршрут `category/<int:category_id>/` и выдаёт `/products/category/1/`.
Ссылки строятся циклом, поэтому id руками писать не нужно. Новая категория из админки сама появится во вкладках.

## Шаг 5. Пагинация — `base_catalog.html`

Номер страницы теперь часть адреса, поэтому ссылки строятся через `{% url %}`. Если категория выбрана — маршрут `category_page`, если нет — `page`.

Пример для кнопки «Вперёд»:

```django
{% if category_id %}
  <a href="{% url 'products:category_page' category_id products.next_page_number %}" class="page-btn">Вперёд ›</a>
{% else %}
  <a href="{% url 'products:page' products.next_page_number %}" class="page-btn">Вперёд ›</a>
{% endif %}
```

Так же меняются «« Первая» (номер `1`), «‹ Назад» (`products.previous_page_number`) и «Последняя »» (`products.paginator.num_pages`).

## Шаг 6. Плитки на главной — `index.html`

Плитки написаны вручную, поэтому здесь id вписывается числом:

```django
<a class="tile" href="{% url 'products:category' 1 %}">   {# 1 — id видеокарт #}
```

Бери числа из админки (см. таблицу в начале). Для категорий, которых ещё нет в базе, оставь `href="#"`.

## Проверка

- `/products/` — все товары, активна вкладка «Все товары».
- `/products/category/1/` — только товары категории с id 1.
- `/products/category/1/page/2/` — вторая страница этой категории (если товаров больше 12).
- `/products/category/99/` — страница 404.

---

# Часть 2. Фильтрация по характеристикам

## Как это работает

- **Характеристики товара — обычные поля в модели `Product`** (`brand`, `socket`, `memory`...).
- **Фильтры передаются GET-запросом**: отмеченная галочка попадает в адрес после `?` (`/products/category/1/?brand=msi`), view читает её из `request.GET`.
- **Шаблон фильтров один на все категории.** Какие группы фильтров показать и какие в них варианты, решает **view**, а шаблон выводит это циклом.

Пример преподавателя («примерно таким»):

```python
# view собирает список фильтров
context = {
    "filters": [
        {"name": "brand",  "title": "Производитель", "values": brands},
        {"name": "socket", "title": "Сокет",         "values": sockets},
    ]
}
```

```django
{# шаблон выводит его двумя циклами #}
{% for filter in filters %}
  <h4>{{ filter.title }}</h4>
  {% for value in filter.values %}
    <input type="checkbox" name="{{ filter.name }}" value="{{ value }}"> {{ value }}
  {% endfor %}
{% endfor %}
```

```python
# view фильтрует через ORM
if request.GET.get("brand"):
    products = products.filter(brand=request.GET["brand"])
```

Это схема. Ниже полная версия, в которой доделано четыре вещи:

1. `get` возвращает только одну галочку. При `?brand=asus&brand=msi` он вернёт только `msi`. Нужны `getlist` и `brand__in`.
2. Вместо отдельного `if` на каждое поле — один цикл по списку фильтров.
3. У каждой категории свой набор фильтров (у видеокарт нет сокета). Нужен словарь «id категории → поля».
4. После «Применить» галочки должны оставаться отмеченными.

## Шаг 1. Поля характеристик — `products/models.py`

```python
class Product(models.Model):
    name = models.CharField(max_length=128, unique=True)
    image = models.ImageField(upload_to="products_media", blank=True)
    description = models.TextField(blank=True)
    short_description = models.TextField(max_length=128, blank=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    quantity = models.PositiveIntegerField(default=0)
    category = models.ForeignKey(ProductCategory, on_delete=models.CASCADE)

    # общие
    brand = models.CharField(max_length=64, blank=True)
    # видеокарты
    series = models.CharField(max_length=32, blank=True)
    memory = models.PositiveIntegerField(null=True, blank=True)
    # процессоры
    socket = models.CharField(max_length=32, blank=True)
    cores = models.PositiveIntegerField(null=True, blank=True)
```

`blank=True` / `null=True` нужны, потому что у процессора поля видеокарты пустые, и наоборот.

```
python manage.py makemigrations
python manage.py migrate
```

## Шаг 2. Заполнить характеристики в админке

Открой каждый товар в `/admin/` и заполни его поля: у видеокарты — бренд, серию, память; у процессора — бренд, сокет, ядра.
Пиши значения одинаково у всех товаров (`MSI`, а не то `MSI`, то `msi`): из этих значений получатся галочки, и разное написание даст две разные галочки.

## Шаг 3. Какие фильтры у какой категории — `products/views.py`

```python
# id категории → список (поле модели, заголовок группы)
CATEGORY_FILTERS = {
    1: [('brand', 'Производитель'), ('series', 'Серия'), ('memory', 'Объём памяти, ГБ')],   # 1 — видеокарты
    2: [('brand', 'Производитель'), ('socket', 'Сокет'), ('cores', 'Количество ядер')],     # 2 — процессоры
}
```

Ключи — id категорий из админки. Здесь id вписывается руками, поэтому подпиши комментарием, какая это категория.

## Шаг 4. Функция, которая собирает фильтры для шаблона

```python
def build_filters(request, products, fields):
    """Собирает список фильтров для шаблона."""
    filters = []
    for name, title in fields:
        values = products.values_list(name, flat=True).distinct().order_by(name)
        filters.append({
            'name': name,
            'title': title,
            'values': [str(v) for v in values if v not in ('', None)],
            'selected': request.GET.getlist(name),
        })
    return filters
```

- `values_list(name, flat=True).distinct()` — все различные значения поля у товаров категории, например `['ASUS', 'MSI']`. Из них получаются галочки, писать варианты руками не нужно.
- `if v not in ('', None)` — у товаров, где поле не заполнено, пустая галочка не появится.
- `str(v)` нужен потому, что `memory` и `cores` — числа, а из адреса приходят строки. Без этого `checked` не сработает: `8` и `"8"` не равны.
- `selected` — что сейчас отмечено. Нужно, чтобы галочки не сбрасывались.

## Шаг 5. Функция, которая применяет фильтры

```python
def apply_filters(request, products, fields):
    """Оставляет только товары, подходящие под отмеченные галочки и цену."""
    for name, _ in fields:
        selected = request.GET.getlist(name)
        if selected:
            products = products.filter(**{f'{name}__in': selected})

    price_min = request.GET.get('price_min')
    price_max = request.GET.get('price_max')
    if price_min:
        products = products.filter(price__gte=price_min)
    if price_max:
        products = products.filter(price__lte=price_max)

    return products
```

- `getlist('brand')` возвращает все отмеченные значения: `['ASUS', 'MSI']`.
- `**{f'{name}__in': selected}` при `name = 'brand'` превращается в `brand__in=selected` — «бренд ASUS или MSI». Так один цикл обслуживает все фильтры.
- Разные группы применяются по очереди, поэтому между ними получается «И»: бренд MSI **и** 8 ГБ.
- Цена — диапазон, а не галочки, поэтому обрабатывается отдельно: `__gte` — «больше или равно», `__lte` — «меньше или равно».

## Шаг 6. Подключить во view

View `products` из части 1 дополняется тремя строками:

```python
def products(request, category_id=None, page_number=1):
    if category_id:
        category = get_object_or_404(ProductCategory, id=category_id)
        products = Product.objects.filter(category_id=category_id)
        category_title = category.name
    else:
        products = Product.objects.all()
        category_title = 'Все товары'

    fields = CATEGORY_FILTERS.get(category_id, [])            # новое
    filtered = apply_filters(request, products, fields)       # новое

    context = {
        'title': 'Каталог',
        'category_title': category_title,
        'category_id': category_id,
        'products': get_products_with_basket(request, filtered, page_number),
        'categories': ProductCategory.objects.all(),
        'filters': build_filters(request, products, fields),  # новое
    }
    return render(request, "products/base_catalog.html", context)
```

- `CATEGORY_FILTERS.get(category_id, [])`: для «Все товары» и для категорий без записи в словаре фильтров по характеристикам не будет, останется только цена.
- В пагинатор идут отфильтрованные товары (`filtered`), а галочки строятся по **всем** товарам категории (`products`). Иначе после выбора MSI галочка ASUS исчезла бы из списка.

## Шаг 7. Общий шаблон фильтров

Создать `products/templates/products/includes/filter_form.html`:

```django
<details class="filter-group" open>
  <summary>Цена</summary>
  <div class="price-range">
    <input type="number" name="price_min" placeholder="от" min="0" value="{{ request.GET.price_min }}">
    <span class="dash">—</span>
    <input type="number" name="price_max" placeholder="до" min="0" value="{{ request.GET.price_max }}">
  </div>
</details>

{% for filter in filters %}
  <details class="filter-group" {% if filter.selected %}open{% endif %}>
    <summary>{{ filter.title }}</summary>
    <div class="filter-options">
      {% for value in filter.values %}
        <label class="checkbox-row">
          <input type="checkbox" name="{{ filter.name }}" value="{{ value }}"
                 {% if value in filter.selected %}checked{% endif %}>
          <span>{{ value }}</span>
        </label>
      {% endfor %}
    </div>
  </details>
{% endfor %}
```

- Внешний цикл — группы (Производитель, Сокет), внутренний — галочки внутри группы.
- `{% if value in filter.selected %}checked{% endif %}` — отмеченные галочки остаются отмеченными после «Применить».
- Цену в поля возвращаем через `request.GET.price_min`.

## Шаг 8. Подключить шаблон — `base_catalog.html`

На место строки, удалённой в части 1 (шаг 3), внутри `<form method="get" action="">`:

```django
{% include 'products/includes/filter_form.html' %}
```

`action=""` значит «отправить на текущий адрес». Если открыта `/products/category/1/`, после «Применить» адрес станет `/products/category/1/?brand=MSI&memory=8` — категория из адреса не теряется.

Файлы `filters_gpu.html`, `filters_cpu.html`, `filters_motherboard.html`, `filters_ram.html`, `filters_ssd.html` больше не нужны.

## Шаг 9. Не терять фильтры при переходе по страницам

Фильтры лежат после `?`, а ссылки пагинации из части 1 (шаг 5) строят адрес без него. Добавь в конец каждой ссылки `{% querystring %}` — он подставит текущие параметры:

```django
<a href="{% url 'products:category_page' category_id products.next_page_number %}{% querystring %}" class="page-btn">Вперёд ›</a>
```

Получится `/products/category/1/page/2/?brand=MSI`.
Если фильтры не выбраны, в конце останется один `?` (`/products/category/1/page/2/?`) — это нормально, страница откроется так же.

А ссылки вкладок категорий (часть 1, шаг 4) оставь **без** `{% querystring %}`: при переходе в другую категорию фильтры должны сбрасываться — у неё другие поля.

## Проверка

- Открыть категорию → в фильтрах видны галочки со значениями из товаров этой категории.
- Отметить две галочки в одной группе → показываются товары с любой из них.
- Отметить галочки в двух группах → только товары, подходящие под обе.
- После «Применить» галочки остались отмеченными, в адресе видны параметры `?brand=...`.
- Перейти на вторую страницу → фильтры сохранились.
- Переключиться на другую категорию → фильтры сбросились.

---

# Как добавить…

**Новую категорию:**
1. Создать её в админке, посмотреть её id.
2. Она сама появится во вкладках. Если нужна плитка на главной — вписать id в `index.html`.
3. Если нужны фильтры — добавить запись `id: [...]` в `CATEGORY_FILTERS`.

**Новый фильтр:**
1. Добавить поле в `Product`, выполнить `makemigrations` и `migrate`.
2. Дописать `('поле', 'Заголовок')` в `CATEGORY_FILTERS` нужной категории.
3. Заполнить поле у товаров в админке.

В шаблоне ничего менять не нужно.

# Плюсы и минусы способа

- ➕ Один view и один шаблон фильтров на все категории.
- ➕ id есть у категории всегда, в модель ничего добавлять не нужно.
- ➕ Варианты фильтров берутся из реальных товаров: нет галочек, по которым ничего не найдётся.
- ➕ Числа хранятся как числа, поэтому легко сделать «больше / меньше» и сортировку.
- ➖ В `CATEGORY_FILTERS` и плитках на главной id вписан числом — надо помнить, что `1` это видеокарты. Если удалить категорию и создать заново, id изменится, и эти места придётся поправить.
- ➖ На странице показывается значение из базы (`MSI`, `8`), а не «8 ГБ». Решение: хранить в базе сразу красивое значение или завести словарь подписей.
- ➖ У процессора пустые поля видеокарты, и каждая новая характеристика требует миграции.

---

# Что сделано в проекте сверх инструкции

- **Все 9 категорий с главной** (id 1–9) и фильтры для каждой — полный список в `CATEGORY_FILTERS` (`products/views.py`). Поля характеристик — в `Product` (`products/models.py`), у каждого поля комментарий, для чего оно.
- **Тестовые товары**: `python manage.py seed_catalog` создаёт категории и по 3 товара в каждой. Команду можно запускать повторно — товары ищутся по названию и обновляются, дубликатов не будет.
- **«В наличии»**: галочка `in_stock`, в `apply_filters` превращается в `quantity__gt=0`.
- **Подсказки в цене**: в `placeholder` самая низкая и самая высокая цена в категории (`price_range` во view, через `aggregate(Min, Max)`).
- **«Сбросить фильтры»** и надпись **«Ничего не найдено»**, если под фильтры ничего не подошло.
- **Группа без значений не показывается**: если ни у одного товара поле не заполнено, заголовок группы не выводится.
- **Сортировка**: словарь `SORTS` во view (`?sort=price`, `price_desc`, `name`). В `order_by` попадает только значение из словаря, неизвестное значение даёт порядок по умолчанию. `<select>` стоит вне формы фильтров, но привязан к ней атрибутом `form="filters-form"`, поэтому сортировка и фильтры отправляются вместе и не сбрасывают друг друга.
- Старые `filters_*.html` удалены.
