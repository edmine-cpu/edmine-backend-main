# Изменения в API v2 для Bids

## Обзор изменений

### 1. **Добавлено поле `main_language` в модель Bid**
   - **Файл**: `models/actions.py`
   - **Поле**: `main_language = fields.CharField(max_length=2, default='en', null=True)`
   - **Описание**: Автоматически определяется при создании бида на основе заполненных полей title/description

### 2. **API v2 - все параметры необязательные**
   - **Файл**: `api/v2/bids.py`
   - **Endpoint**: `GET /api/v2/` (вместо `GET /api/v2/{language}/{country}/{city}/{category}/{subcategory}/`)
   - **Query параметры** (все опциональные):
     - `language` - язык (uk, en, pl, de, fr), дефолт: `en`
     - `country` - slug страны
     - `city` - slug города
     - `category` - slug категории
     - `subcategory` - slug подкатегории
     - `search` - текстовый поиск
     - `min_cost` - минимальная цена
     - `max_cost` - максимальная цена

### 3. **Автоопределение языка при создании**
   - **Файлы**: `services/bids/service.py`
   - **Методы**: `create_request()` и `create_request_fast()`
   - **Логика**: Использует функцию `detect_primary_language()` из `services/translation/utils.py`
   - **Приоритет**: uk > en > pl > fr > de

### 4. **Обновлен сервис получения бидов**
   - **Файл**: `services/v2/bids.py`
   - **Изменения**:
     - Все фильтры опциональные
     - Использует `bid.main_language` для отображения данных
     - Fallback на английский если язык не определен

## Миграция БД

### Применение миграции:

```bash
# Подключитесь к PostgreSQL
psql -U postgres -d makeasap_dev

# Выполните миграцию
\i migrations/add_main_language_to_bids.sql
```

Миграция автоматически:
1. Добавит колонку `main_language`
2. Создаст индекс для оптимизации
3. Определит язык для существующих бидов
4. Выведет статистику

## Добавление тестовых данных

### Запуск скрипта:

```bash
python scripts/add_test_bids.py
```

Скрипт создаст 8 тестовых бидов на разных языках (uk, en, pl, de, fr) с валидными связями из БД.

**Требования**:
- В БД должны быть пользователи, страны, города, категории, подкатегории
- Скрипт автоматически получит существующие ID и создаст валидные связи

## Примеры использования API v2

### Получить все биды (английский язык по умолчанию):
```bash
GET /api/v2/
```

### Получить биды на украинском:
```bash
GET /api/v2/?language=uk
```

### Фильтр по стране и категории:
```bash
GET /api/v2/?language=uk&country=ukraine&category=programming
```

### Полный фильтр с ценой и поиском:
```bash
GET /api/v2/?language=en&country=poland&city=warsaw&category=design&subcategory=logo&search=startup&min_cost=100&max_cost=1000
```

## Ответ API

```json
{
  "country": "Poland",
  "city": "Warsaw",
  "category": "Design",
  "subcategory": "Logo Design",
  "lang_search": "en",
  "min_cost": 100,
  "max_cost": 1000,
  "results": [
    {
      "title": "Logo Design for Startup",
      "subcprice": "500",
      "category": [3],
      "undercategory": [12],
      "country": "Poland",
      "city": "Warsaw",
      "slug": "logo-design-for-startup-2",
      "owner_id": 5
    }
  ],
  "total": 1
}
```

## Безопасность

Все изменения обеспечивают:
- ✅ Защита от SQL-инъекций через ORM
- ✅ Валидация всех входных параметров через Pydantic
- ✅ Безопасная работа с JSONField
- ✅ Индексы для оптимизации запросов

## Обратная совместимость

- Старый API (`/api/bids`) работает без изменений
- Новый API v2 (`/api/v2/`) - опциональные параметры
- Существующие биды получат `main_language = 'en'` при миграции
