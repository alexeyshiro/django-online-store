# Проверка совместимости в конфигураторе

Цель: когда в сборке есть товары, которые не будут работать вместе, конфигуратор должен показать,
**что именно не так**. Например:

> ❌ Процессор **AMD Ryzen 5 7600** (сокет AM5) не подходит к материнской плате **GIGABYTE A520M K V2** (сокет AM4).
> ⚠️ Блок питания **DeepCool PK650D 650 Вт** слабоват: сборке нужно около 720 Вт.

Документ из четырёх частей:

1. Что вообще нужно проверять в ПК: полный список правил.
2. Каких данных для этого не хватает в проекте.
3. Варианты реализации, их плюсы и минусы.
4. Пошаговая реализация рекомендуемого варианта.

---

# Честно про «гарантированно работает»

Проверка может дать гарантию только в пределах тех данных, что лежат в базе. Если в базе не указано,
например, высота кулера и сколько места под кулер в корпусе, программа не сможет понять, что крышка не закроется.

Поэтому:

- **Полная проверка = полные данные.** Для каждого правила ниже указано, какие поля нужны. Пока поле не заполнено у товара, проверка по нему невозможна. Об этом тоже надо честно сообщать («не удалось проверить: у корпуса не указана максимальная длина видеокарты»), а не молча считать сборку совместимой.
- **Некоторые вещи проверить по характеристикам нельзя в принципе**: версия BIOS на конкретной плате со склада, упирается ли высокий радиатор памяти в башенный кулер, качество питания платы для топового процессора. Магазины решают это списками проверенных сочетаний от производителя (QVL, списки поддерживаемых процессоров). Это вариант В ниже.

Итог: проверка делится на **ошибки** (точно не заработает), **предупреждения** (заработает с оговорками) и **«не удалось проверить»** (не хватает данных).

---

# Часть 1. Что проверять: полный список правил

Уровни:
- ❌ **ошибка** — собрать или запустить нельзя;
- ⚠️ **предупреждение** — заработает, но с оговоркой (нужно обновить BIOS, память будет работать медленнее, блок питания без запаса).

| № | Что с чем | Правило | Уровень | Нужные поля |
|---|---|---|---|---|
| 1 | Процессор ↔ материнская плата | сокеты совпадают | ❌ | `socket` (есть) |
| 2 | Процессор ↔ материнская плата | чипсет платы поддерживает этот процессор (напр. A520 + Ryzen 9000 — нет; B660 + Core 14-го поколения — только после обновления BIOS) | ❌ / ⚠️ | список поддерживаемых серий у чипсета (нет) |
| 3 | Материнская плата ↔ память | тип памяти совпадает (DDR4 / DDR5) | ❌ | `memory_type` (есть) |
| 4 | Материнская плата ↔ память | память для ПК (DIMM), а не для ноутбука (SO-DIMM) | ❌ | `form_factor` у памяти (есть) |
| 5 | Материнская плата ↔ память | модулей не больше, чем слотов | ❌ | `modules`, `memory_slots` (есть) |
| 6 | Материнская плата ↔ память | объём не больше максимума платы | ❌ | `max_memory` у платы (нет) |
| 7 | Процессор ↔ память | процессор поддерживает этот тип памяти (Intel 12–14 умеют DDR4 и DDR5, AMD AM5 — только DDR5) | ❌ | у процессора **список** типов (сейчас одно значение) |
| 8 | Память ↔ плата/процессор | частота выше поддерживаемой — будет работать на меньшей | ⚠️ | `frequency`, `max_memory_frequency` (нет) |
| 9 | Материнская плата ↔ корпус | форм-фактор платы помещается в корпус (ITX < mATX < ATX < E-ATX) | ❌ | `form_factor` у платы, `mb_support` у корпуса (есть) |
| 10 | Видеокарта ↔ корпус | длина видеокарты ≤ максимальной длины в корпусе | ❌ | `length` у видеокарты, `max_gpu_length` у корпуса (нет) |
| 11 | Кулер ↔ процессор | кулер поддерживает сокет процессора | ❌ | у кулера **список** сокетов (нет) |
| 12 | Кулер ↔ процессор | рассеиваемая мощность кулера ≥ тепловыделения процессора | ⚠️ | `tdp` у обоих (есть) |
| 13 | Кулер ↔ корпус | высота башенного кулера ≤ максимальной в корпусе | ❌ | `height`, `max_cooler_height` (нет) |
| 14 | СЖО ↔ корпус | корпус поддерживает радиатор такого размера (240 / 280 / 360) | ❌ | `radiator_size`, список у корпуса (нет) |
| 15 | Блок питания ↔ вся сборка | мощности хватает: ошибка, если меньше потребления; предупреждение, если запас < 30 % | ❌ / ⚠️ | `power` (есть), `tdp` процессора (есть), `tdp` видеокарты (нет) |
| 16 | Блок питания ↔ видеокарта | есть нужный разъём питания (12V-2x6 / 16-pin для RTX 40–50) | ⚠️ (через переходник) | `connector_12v` у БП (есть), `power_connector` у видеокарты (нет) |
| 17 | Блок питания ↔ корпус | форм-фактор БП подходит корпусу (ATX / SFX) | ❌ | `form_factor` у БП (есть), список у корпуса (нет) |
| 18 | Накопитель ↔ материнская плата | для M.2 SSD на плате есть M.2-слот; для SATA — SATA-порт | ❌ | `drive_type` (есть), `m2_slots`, `sata_ports` (нет) |
| 19 | Накопитель / видеокарта ↔ плата | версия PCIe ниже — будет работать медленнее | ⚠️ | `pcie`, `interface` (есть), версия у платы (нет) |
| 20 | Процессор без видеокарты | если видеокарта не выбрана, у процессора должна быть встроенная графика, иначе нет изображения | ❌ | `integrated_graphics` (есть) |
| 21 | Вентиляторы ↔ корпус | размер (120 / 140) поддерживается, штук не больше мест | ❌ / ⚠️ | `fan_size`, `pack_count` (есть), места в корпусе (нет) |
| 22 | Сборка целиком | выбраны все обязательные комплектующие | ❌ | — (`CONFIG_REQUIRED` уже есть) |

Сразу, на имеющихся полях, можно сделать правила **1, 3, 4, 5, 9, 12, 20, 22**. Правило 15 заработает частично, по одному процессору.
Для остальных нужно добавить поля (часть 2).

---

# Часть 2. Каких данных не хватает

## Одиночные поля — добавляются как обычно

По способу преподавателя, обычными полями в `Product`:

```python
# видеокарты
length = models.PositiveIntegerField(null=True, blank=True)            # длина, мм
gpu_tdp = models.PositiveIntegerField(null=True, blank=True)           # потребление, Вт
power_connector = models.CharField(max_length=32, blank=True)          # 8-pin, 2x8-pin, 12V-2x6

# материнские платы
max_memory = models.PositiveIntegerField(null=True, blank=True)        # макс. объём памяти, ГБ
m2_slots = models.PositiveIntegerField(null=True, blank=True)
sata_ports = models.PositiveIntegerField(null=True, blank=True)

# охлаждение
height = models.PositiveIntegerField(null=True, blank=True)            # высота башни, мм
radiator_size = models.PositiveIntegerField(null=True, blank=True)     # 240 / 280 / 360

# корпусы
max_gpu_length = models.PositiveIntegerField(null=True, blank=True)    # мм
max_cooler_height = models.PositiveIntegerField(null=True, blank=True) # мм
```

## Поля со списком значений — главная сложность

У кулера не один сокет, а десяток (`AM4, AM5, LGA1700, LGA1851`). Процессор Intel поддерживает и DDR4, и DDR5.
Корпус держит радиаторы 240 и 360. В поле `CharField` помещается только одно значение, поэтому есть три способа:

| Способ | Как выглядит | Плюсы | Минусы |
|---|---|---|---|
| **Текст через запятую** | `sockets = CharField()` → `"AM4, AM5, LGA1700"`, в коде `split(',')` | проще всего, одно поле, заполняется в админке одной строкой | опечатки не ловятся (`AM 5`), фильтр по такому полю неудобный |
| **ManyToMany на справочник** | модель `Socket(name)`, у товара `sockets = ManyToManyField(Socket)` | в админке выбор из списка, опечаток нет, фильтр `sockets__name='AM5'` | отдельная модель и миграция на каждый справочник |
| **JSONField со списком** | `sockets = JSONField(default=list)` → `["AM4", "AM5"]` | гибко, одно поле | в стандартной админке неудобно редактировать, значения не проверяются |

Для учебного проекта хватит **текста через запятую** с одной функцией-помощником:

```python
def as_list(value):
    """'AM4, AM5 ,LGA1700' → {'AM4', 'AM5', 'LGA1700'}"""
    return {item.strip() for item in value.split(',') if item.strip()}
```

Если нужно «как в настоящем магазине» — **ManyToMany**.

Какие поля становятся списками: `sockets` у кулера, `memory_types` у процессора,
`radiator_support` и `psu_support` у корпуса, `supported_series` у чипсета (или у платы).

---

# Часть 3. Варианты реализации

## Вариант А. Правила в Python-коде (рекомендуется)

Отдельный файл `products/compatibility.py`. Каждое правило — маленькая функция: получает сборку
и возвращает список проблем с понятным текстом.

```python
def check_cpu_motherboard(build):
    cpu, board = build.get('cpu'), build.get('motherboard')
    if cpu and board and cpu.socket != board.socket:
        return [error(f'Процессор {cpu.name} (сокет {cpu.socket}) не подходит '
                      f'к материнской плате {board.name} (сокет {board.socket})')]
    return []
```

- ➕ Любое правило любой сложности: сравнение, сумма мощностей, иерархия форм-факторов, «если нет видеокарты, то…».
- ➕ Текст ошибки пишется прямо рядом с правилом, поэтому легко сказать «что именно не так».
- ➕ Легко тестировать: подсунул два товара — проверил результат.
- ➖ Новое правило = правка кода (но правила меняются редко: сокеты и форм-факторы — это физика, а не настройки магазина).

## Вариант Б. Правила как данные (таблица правил)

Правило описывается строкой в словаре или в базе: «поле `socket` у `cpu` должно быть равно полю `socket` у `motherboard`».

```python
RULES = [
    # (строка 1, поле 1, операция, строка 2, поле 2, уровень, текст)
    ('cpu', 'socket', 'eq', 'motherboard', 'socket', 'error', 'Сокет процессора и платы не совпадает'),
    ('motherboard', 'memory_type', 'eq', 'ram', 'memory_type', 'error', 'Тип памяти не совпадает'),
    ('ram', 'modules', 'lte', 'motherboard', 'memory_slots', 'error', 'Модулей больше, чем слотов'),
    ('cpu', 'socket', 'in', 'cooling', 'sockets', 'error', 'Кулер не поддерживает сокет процессора'),
]
```

Одна общая функция проходит по списку и применяет операции `eq`, `lte`, `in`.

- ➕ Простые правила добавляются одной строкой, а если хранить их в базе — даже через админку, без программиста.
- ➖ Сложные правила так не описать: мощность блока питания (сумма по нескольким товарам), иерархия форм-факторов, «встроенная графика нужна, только если нет видеокарты». Их всё равно придётся писать кодом, то есть получится вариант А + Б.
- ➖ Тексты ошибок получаются шаблонными.

## Вариант В. Явная таблица совместимых пар (whitelist)

Модель `Compatibility(product_a, product_b)`: администратор вручную отмечает, какие товары **проверены** вместе.
Так магазины хранят данные из QVL (списков проверенных модулей памяти от производителя платы)
и списков поддерживаемых процессоров.

- ➕ Единственный способ приблизиться к **настоящей** гарантии: проверено человеком или производителем, а не выведено из характеристик.
- ➕ Ловит то, что по характеристикам не видно (BIOS, конкретные модели памяти).
- ➖ Очень много ручной работы: пар «процессор × плата» — сотни, «память × плата» — тысячи.
- ➖ Новый товар несовместим ни с чем, пока его не внесут в таблицу.

Разумно использовать **поверх** варианта А и только для самых капризных пар (процессор ↔ чипсет, память ↔ плата):
правила А отсекают явно несовместимое, таблица В подтверждает, что «проверено производителем».

## Вариант Г. Проверка в браузере на JavaScript

Те же правила, но на JS, чтобы ошибка появлялась без перезагрузки страницы.

- ➕ Мгновенный отклик.
- ➖ Правила придётся писать дважды: на сервере они всё равно нужны, потому что JS можно отключить или обойти, а корзину и заказ проверяет сервер.
- ➖ В проекте конфигуратор и так перезагружается после каждого действия (формы POST), поэтому выигрыша почти нет.

Имеет смысл только вместе с AJAX, а не вместо проверки на сервере.

**Для этого проекта не подходит:** на сайте договорились обходиться без JavaScript — только HTML, CSS, Django и Python.

## Вариант Д. Готовые сервисы

Самый известный сервис с проверкой совместимости — PCPartPicker, но открытого API у него нет.
Российские магазины своих правил не публикуют. Для учебного проекта этот вариант отпадает, данные всё равно придётся хранить у себя.

## Где показывать результат проверки

Это не отдельный вариант, а решение поверх любого из них:

| Где | Что показывать |
|---|---|
| **Конфигуратор** | список проблем над сборкой, красная рамка у несовместимых строк, итог «Сборка совместима ✓» |
| **Сообщение после «В конфигуратор»** | «Товар добавлен, но не подходит: другой сокет» — через `django.contrib.messages` |
| **Каталог, открытый из конфигуратора** | у каждой карточки пометка «Не подходит к вашей сборке: сокет AM4, нужен AM5», или галочка «Только совместимые» |
| **Кнопка «Добавить в корзину» сборки** | при ошибках (❌) не давать добавить или спрашивать подтверждение; предупреждения (⚠️) не мешают |

## Сравнение

| | А. Код | Б. Таблица правил | В. Пары вручную | Г. JS |
|---|---|---|---|---|
| Сложность | ⭐⭐ | ⭐⭐⭐ | ⭐⭐ (код) + много ручной работы | ⭐⭐⭐ |
| Любые правила (суммы, «если нет…») | ✅ | ❌ только простые | ❌ только пары | ✅ |
| Понятный текст «что не так» | ✅ | ⚠️ шаблонный | ⚠️ «не проверено» | ✅ |
| Новое правило без программиста | ❌ | ✅ | ✅ | ❌ |
| Ловит то, чего нет в характеристиках | ❌ | ❌ | ✅ | ❌ |
| Нужен на сервере всё равно | — | — | — | ✅ дублирование |

**Рекомендация:** вариант **А**, а если захочется «как у больших магазинов» — добавить **В** для пары процессор ↔ чипсет.

---

# Часть 4. Как сделать вариант А по шагам

## Шаг 1. Добавить недостающие поля

Поля из части 2 — в `Product`, затем `makemigrations` и `migrate`.
Заполнить их у товаров: можно в админке, можно дописать в команду `seed_catalog`.
Добавить новые поля в `CATEGORY_FILTERS`, тогда они появятся и в фильтрах, и на странице товара.

## Шаг 2. Файл с правилами — `products/compatibility.py`

```python
"""
Проверка совместимости сборки.
build — словарь {ключ строки конфигуратора: товар}, например {'cpu': <Product>, 'motherboard': <Product>}.
Для строк, где можно выбрать несколько товаров (CONFIG_MULTI, сейчас это 'storage' и 'fans'), значение — список товаров.
Ключи те же, что в CONFIG_SLOTS (products/views.py).
"""
from dataclasses import dataclass, field


@dataclass
class Problem:
    level: str                                   # 'error' | 'warning' | 'unknown'
    message: str                                 # что именно не так — показывается пользователю
    slots: list = field(default_factory=list)    # какие строки конфигуратора подсветить


def error(message, *slots):
    return Problem('error', message, list(slots))


def warning(message, *slots):
    return Problem('warning', message, list(slots))


def unknown(message, *slots):
    return Problem('unknown', message, list(slots))


def as_list(value):
    """'AM4, AM5' → {'AM4', 'AM5'}"""
    return {item.strip() for item in (value or '').split(',') if item.strip()}


# Размеры форм-факторов плат: чем больше число, тем больше плата
BOARD_SIZE = {'Mini-ITX': 1, 'Micro-ATX': 2, 'ATX': 3, 'E-ATX': 4}


# ---------- правила ----------

def check_cpu_motherboard(b):
    cpu, board = b.get('cpu'), b.get('motherboard')
    if not (cpu and board):
        return []
    if cpu.socket != board.socket:
        return [error(f'Процессор «{cpu.name}» (сокет {cpu.socket}) не подходит к материнской плате '
                      f'«{board.name}» (сокет {board.socket}).', 'cpu', 'motherboard')]
    return []


def check_memory(b):
    ram, board, cpu = b.get('ram'), b.get('motherboard'), b.get('cpu')
    problems = []
    if ram and board:
        if ram.memory_type != board.memory_type:
            problems.append(error(f'Память «{ram.name}» — {ram.memory_type}, а плата «{board.name}» '
                                  f'поддерживает только {board.memory_type}.', 'ram', 'motherboard'))
        if ram.form_factor == 'SO-DIMM':
            problems.append(error(f'«{ram.name}» — память для ноутбуков (SO-DIMM), в слоты ПК она не встанет.',
                                  'ram'))
        if ram.modules and board.memory_slots and ram.modules > board.memory_slots:
            problems.append(error(f'В комплекте {ram.modules} модуля, а на плате «{board.name}» '
                                  f'только {board.memory_slots} слота.', 'ram', 'motherboard'))
    if ram and cpu and cpu.memory_type and ram.memory_type not in as_list(cpu.memory_type):
        problems.append(error(f'Процессор «{cpu.name}» не поддерживает память {ram.memory_type}.', 'ram', 'cpu'))
    return problems


def check_case_board(b):
    case, board = b.get('case'), b.get('motherboard')
    if not (case and board):
        return []
    board_size, case_size = BOARD_SIZE.get(board.form_factor), BOARD_SIZE.get(case.mb_support)
    if board_size is None or case_size is None:
        return [unknown(f'Не удалось проверить, помещается ли плата в корпус: не указан форм-фактор.',
                        'case', 'motherboard')]
    if board_size > case_size:
        return [error(f'Плата «{board.name}» ({board.form_factor}) не поместится в корпус «{case.name}»: '
                      f'он рассчитан максимум на {case.mb_support}.', 'case', 'motherboard')]
    return []


def check_gpu_case(b):
    gpu, case = b.get('gpu'), b.get('case')
    if not (gpu and case):
        return []
    if not (gpu.length and case.max_gpu_length):
        return [unknown('Не удалось проверить длину видеокарты: не указаны размеры.', 'gpu', 'case')]
    if gpu.length > case.max_gpu_length:
        return [error(f'Видеокарта «{gpu.name}» длиной {gpu.length} мм не поместится в корпус «{case.name}» '
                      f'(максимум {case.max_gpu_length} мм).', 'gpu', 'case')]
    return []


def check_cooler(b):
    cooler, cpu, case = b.get('cooling'), b.get('cpu'), b.get('case')
    problems = []
    if cooler and cpu:
        if cpu.socket not in as_list(cooler.sockets):
            problems.append(error(f'Кулер «{cooler.name}» не крепится на сокет {cpu.socket}.', 'cooling', 'cpu'))
        if cooler.tdp and cpu.tdp and cooler.tdp < cpu.tdp:
            problems.append(warning(f'Кулер рассчитан на {cooler.tdp} Вт, а процессор выделяет {cpu.tdp} Вт — '
                                    f'возможен перегрев и снижение частот.', 'cooling', 'cpu'))
    if cooler and case and cooler.height and case.max_cooler_height and cooler.height > case.max_cooler_height:
        problems.append(error(f'Кулер высотой {cooler.height} мм не поместится в корпус «{case.name}» '
                              f'(максимум {case.max_cooler_height} мм).', 'cooling', 'case'))
    return problems


def check_power(b):
    psu = b.get('psu')
    if not psu:
        return []
    cpu, gpu = b.get('cpu'), b.get('gpu')
    need = 75                                   # плата, память, диски, вентиляторы — с запасом
    if cpu:
        need += cpu.tdp or 0
    if gpu:
        if not gpu.gpu_tdp:
            return [unknown('Не удалось посчитать мощность: у видеокарты не указано потребление.', 'psu', 'gpu')]
        need += gpu.gpu_tdp
    recommended = round(need * 1.3)             # запас 30 % на пиковые нагрузки

    if psu.power < need:
        return [error(f'Блоку питания «{psu.name}» ({psu.power} Вт) не хватит мощности: '
                      f'сборка потребляет около {need} Вт.', 'psu')]
    if psu.power < recommended:
        return [warning(f'Блок питания {psu.power} Вт — почти без запаса. Рекомендуется от {recommended} Вт.',
                        'psu')]
    return []


def check_graphics_output(b):
    cpu = b.get('cpu')
    if cpu and not b.get('gpu') and cpu.integrated_graphics != 'Есть':
        return [error(f'У процессора «{cpu.name}» нет встроенной графики — без видеокарты не будет изображения.',
                      'cpu', 'gpu')]
    return []


def check_storage(b):
    # накопителей в сборке может быть несколько (CONFIG_MULTI), поэтому здесь список
    drives, board = b.get('storage', []), b.get('motherboard')
    if not (drives and board):
        return []
    m2_drives = [d for d in drives if d.drive_type == 'SSD M.2']
    sata_drives = [d for d in drives if d.interface == 'SATA III']
    problems = []
    if board.m2_slots is not None and len(m2_drives) > board.m2_slots:
        problems.append(error(f'Выбрано {len(m2_drives)} M.2 SSD, а на плате «{board.name}» '
                              f'только {board.m2_slots} слота M.2.', 'storage', 'motherboard'))
    if board.sata_ports is not None and len(sata_drives) > board.sata_ports:
        problems.append(error(f'Выбрано {len(sata_drives)} SATA-накопителя, а на плате «{board.name}» '
                              f'только {board.sata_ports} SATA-порта.', 'storage', 'motherboard'))
    return problems


RULES = [
    check_cpu_motherboard,
    check_memory,
    check_case_board,
    check_gpu_case,
    check_cooler,
    check_power,
    check_graphics_output,
    check_storage,
]


def check_build(build):
    """Все проблемы сборки: сначала ошибки, потом предупреждения, потом «не удалось проверить»."""
    problems = []
    for rule in RULES:
        problems += rule(build)
    order = {'error': 0, 'warning': 1, 'unknown': 2}
    return sorted(problems, key=lambda p: order[p.level])
```

Как это устроено:
- Каждое правило проверяет **только свою пару** и молчит, если одного из товаров нет в сборке (`if not (cpu and board): return []`).
  Поэтому проверку можно запускать на неполной сборке, пока пользователь её собирает.
- Если нужного поля нет, правило не делает вид, что всё хорошо, а возвращает `unknown` — «не удалось проверить».
- Текст ошибки собирается из названий и значений конкретных товаров, поэтому видно, что именно не так.
- Новое правило = новая функция + одна строка в `RULES`.

## Шаг 3. Вызвать проверку во view конфигуратора

В `config` (`products/views.py`) сборка уже собрана в `slots`. Нужно:

```python
from products.compatibility import check_build

    # в строках из CONFIG_MULTI (накопители, вентиляторы) — список товаров, в остальных — один товар
    build = {}
    for key, slot in slots.items():
        if slot['multi']:
            build[key] = slot['products']
        elif slot['product']:
            build[key] = slot['product']
    problems = check_build(build)

    # чтобы подсветить строки конфигуратора
    for problem in problems:
        for key in problem.slots:
            if key in slots and problem.level == 'error':
                slots[key]['has_error'] = True

    context.update({
        'problems': problems,
        'has_errors': any(p.level == 'error' for p in problems),
    })
```

И дописать в `config_add` сообщение, чтобы пользователь сразу узнал о проблеме:

```python
from django.contrib import messages

    # после сохранения товара в сессию
    build = {...}                       # как выше, но уже с новым товаром
    for problem in check_build(build):
        if problem.level == 'error' and CONFIG_KEY_BY_CATEGORY[product.category_id] in problem.slots:
            messages.warning(request, f'Товар добавлен, но есть проблема: {problem.message}')
```

## Шаг 4. Показать в шаблоне `configurator.html`

Над списком комплектующих:

```django
{% if problems %}
  <div class="compat">
    {% for problem in problems %}
      <div class="compat-item {{ problem.level }}">
        {% if problem.level == 'error' %}❌{% elif problem.level == 'warning' %}⚠️{% else %}❔{% endif %}
        {{ problem.message }}
      </div>
    {% endfor %}
  </div>
{% elif selected_count > 1 %}
  <div class="compat ok">✓ Все выбранные комплектующие совместимы</div>
{% endif %}
```

Строку с ошибкой подсветить: в `configurator.html` у нужного `comp-row` добавить класс,
`{% if slots.cpu.has_error %}comp-row-error{% endif %}`, и в CSS сделать красную рамку слева.

Кнопку «Добавить в корзину» при ошибках заблокировать:

```django
{% if has_errors %}
  <button type="button" class="buy-btn" disabled>Исправьте ошибки совместимости</button>
{% elif ... %}
```

## Шаг 5 (по желанию). Пометки в каталоге

Когда пользователь нажал «Добавить» или «Заменить» в конфигураторе и попал в каталог,
для каждой карточки можно проверить: «а что, если поставить этот товар в сборку?»

```python
build = текущая сборка из сессии
key = ключ строки для этой категории ('cpu', 'gpu', ...)
for product in page.object_list:
    test_build = {**build, key: product}
    product.compat_errors = [p.message for p in check_build(test_build)
                             if p.level == 'error' and key in p.slots]
```

В карточке:

```django
{% if product.compat_errors %}
  <span class="product-incompatible" title="{{ product.compat_errors|join:' ' }}">Не подходит к сборке</span>
{% endif %}
```

А галочка «Только совместимые» в фильтрах просто оставляет товары с пустым `compat_errors`.
Для каталога на несколько сотен товаров это быстро: проверка идёт в Python и не делает запросов к базе.

## Шаг 6. Тесты

Правила легко проверить без браузера, на объектах `Product`, которые даже не нужно сохранять в базу:

```python
from django.test import SimpleTestCase
from products.models import Product
from products.compatibility import check_build


class CompatibilityTests(SimpleTestCase):
    def test_socket_mismatch(self):
        cpu = Product(name='Ryzen 5 7600', socket='AM5')
        board = Product(name='A520M', socket='AM4')
        problems = check_build({'cpu': cpu, 'motherboard': board})
        self.assertEqual(problems[0].level, 'error')
        self.assertIn('AM4', problems[0].message)

    def test_same_socket_ok(self):
        cpu = Product(name='Ryzen 5 7600', socket='AM5')
        board = Product(name='B650', socket='AM5')
        self.assertEqual(check_build({'cpu': cpu, 'motherboard': board}), [])
```

Запуск: `python manage.py test products`.

---

# Что даст проверка на текущих тестовых товарах

Правила, которым хватает уже существующих полей (1, 3, 4, 5, 9, 12, 20), найдут реальные проблемы в тестовых товарах:

| Сборка | Результат |
|---|---|
| Ryzen 5 7600 (AM5) + GIGABYTE A520M (AM4) | ❌ сокет не совпадает |
| MSI B650 (DDR5) + Crucial DDR4 SO-DIMM | ❌ другой тип памяти и ❌ память для ноутбука |
| Intel Core i5-14600KF без видеокарты | ❌ нет встроенной графики |
| MSI B650 (ATX) + Cooler Master Q300L (до Micro-ATX) | ❌ плата не поместится в корпус |
| Ryzen 7 9800X3D (120 Вт) + DeepCool AK400 (220 Вт) | ✓ по мощности кулера (сокет проверится после добавления поля `sockets`) |

**Важно:** код из шага 2 обращается и к новым полям (`sockets`, `length`, `gpu_tdp`, `height`, `m2_slots`...).
Пока их нет в модели, будет ошибка `AttributeError`. Поэтому либо сначала сделать шаг 1, либо временно
убрать из `RULES` правила `check_gpu_case`, `check_cooler`, `check_power` и `check_storage`.
Остальные правила работают на существующих полях.

---

# Итог: порядок работы

1. Решить, как хранить списки значений: текст через запятую или ManyToMany (часть 2).
2. Добавить недостающие поля и заполнить их у товаров.
3. Создать `products/compatibility.py` с правилами (шаг 2). Начать с правил, для которых данные уже есть: 1, 3, 4, 5, 9, 12, 20.
4. Вызвать `check_build` в конфигураторе и вывести проблемы (шаги 3–4).
5. По желанию: пометки «не подходит» в каталоге (шаг 5) и тесты (шаг 6).
6. Если нужна гарантия «проверено производителем» — добавить таблицу совместимых пар (вариант В) для процессора и чипсета.
