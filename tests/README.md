# Автотесты для Edmine Backend

Комплексный набор автотестов для всех API эндпоинтов проекта.

## Структура тестов

```
tests/
├── __init__.py
├── conftest.py              # Фикстуры и настройки для всех тестов
├── test_blog.py            # Тесты для блога
├── test_company.py         # Тесты для компаний
├── test_bids.py            # Тесты для заявок (bids)
├── test_user.py            # Тесты для пользователей
└── test_admin.py           # Тесты для админ-панели
```

## Установка зависимостей

```bash
# Установка зависимостей для тестирования
pip install -r requirements-dev.txt
```

## Запуск тестов

### Запуск всех тестов
```bash
pytest
```

### Запуск тестов с подробным выводом
```bash
pytest -v
```

### Запуск тестов для конкретного модуля
```bash
# Тесты блога
pytest tests/test_blog.py

# Тесты компаний
pytest tests/test_company.py

# Тесты заявок
pytest tests/test_bids.py

# Тесты пользователей
pytest tests/test_user.py

# Тесты админки
pytest tests/test_admin.py
```

### Запуск конкретного теста
```bash
pytest tests/test_blog.py::TestBlogEndpoints::test_get_blog_articles_default_params
```

### Запуск с покрытием кода
```bash
pytest --cov=. --cov-report=html
```

### Запуск с определенными маркерами
```bash
# Только быстрые тесты
pytest -m "not slow"

# Только smoke тесты
pytest -m smoke

# Только integration тесты
pytest -m integration
```

## Описание тестовых модулей

### test_blog.py
Тесты для API блога:
- Получение списка статей
- Получение статьи по ID
- Фильтрация по языкам (uk, en, pl, fr, de)
- Пагинация
- Проверка публикации статей

**Основные эндпоинты:**
- `GET /api/blog/articles`
- `GET /api/blog/articles/{article_id}`

### test_company.py
Тесты для API компаний:
- Получение списка компаний
- Получение компании по ID
- Получение компании по slug
- Создание компании
- Обновление компании
- Удаление компании
- Фильтрация по категориям и локации
- Поиск компаний

**Основные эндпоинты:**
- `GET /api/companies`
- `GET /api/companies/{company_id}`
- `GET /api/companies/slug/{slug_with_id}`
- `POST /api/companies`
- `POST /api/companies-fast`
- `PUT /api/companies/{company_id}`
- `DELETE /api/companies/{company_id}`

### test_bids.py
Тесты для API заявок:
- Получение списка заявок
- Получение заявки по ID
- Создание заявки
- Создание заявки с файлами
- Верификация заявки по коду
- Отправка ответа на заявку
- Удаление заявки
- Фильтрация и сортировка

**Основные эндпоинты:**
- `GET /api/bids`
- `GET /api/bids/{bid_id}`
- `POST /api/{lang}/create-request`
- `POST /api/{lang}/create-request-fast`
- `POST /api/{lang}/verify-request-code`
- `POST /api/submit-response`
- `DELETE /api/bid/{bid_id}`

### test_user.py
Тесты для API пользователей:
- Регистрация пользователя
- Вход в систему
- Выход из системы
- Получение списка пользователей
- Получение пользователя по ID
- Получение текущего пользователя
- Верификация email
- Проверка валидации данных

**Основные эндпоинты:**
- `GET /api/users`
- `GET /api/user/{id}`
- `POST /api/register`
- `POST /api/login`
- `POST /api/logout`
- `POST /api/verify-code`
- `GET /api/me`

### test_admin.py
Тесты для админ-панели:
- Статистика системы
- Управление пользователями
- Управление блогами
- Управление заявками
- Управление чатами
- Управление заблокированными IP
- Проверка прав доступа

**Основные эндпоинты:**
- `GET /api/admin/stats`
- `GET /api/admin/dashboard`
- `GET /api/admin/users`
- `PUT /api/admin/users/{user_id}`
- `DELETE /api/admin/users/{user_id}`
- `GET /api/admin/blogs`
- `DELETE /api/admin/blogs/{blog_id}`
- `GET /api/admin/bids`
- `GET /api/admin/chats`
- `GET /api/admin/banned-ips`
- `POST /api/admin/ban-ip`
- `DELETE /api/admin/unban-ip/{ip_id}`

## Фикстуры (conftest.py)

Доступные фикстуры для использования в тестах:

- `client` - HTTP клиент для тестирования API
- `init_db` - Инициализация тестовой базы данных
- `test_user` - Тестовый пользователь
- `test_admin` - Тестовый администратор
- `test_company` - Тестовая компания
- `test_category` - Тестовая категория
- `test_subcategory` - Тестовая подкатегория
- `test_country` - Тестовая страна
- `test_city` - Тестовый город
- `test_bid` - Тестовая заявка
- `test_blog_article` - Тестовая статья блога
- `authenticated_client` - Аутентифицированный клиент
- `admin_client` - Клиент с правами администратора

## Конфигурация базы данных

Тесты используют отдельную тестовую базу данных `makeasap_test`.
Убедитесь, что база данных создана перед запуском тестов:

```bash
# Создание тестовой базы данных
createdb makeasap_test

# Или через psql
psql -U postgres -c "CREATE DATABASE makeasap_test;"
```

## Покрытие кода

Для просмотра покрытия кода:

```bash
# Запуск тестов с покрытием
pytest --cov=. --cov-report=html

# Открыть отчет в браузере
open htmlcov/index.html  # на macOS
xdg-open htmlcov/index.html  # на Linux
start htmlcov/index.html  # на Windows
```

## Непрерывная интеграция (CI/CD)

Тесты можно интегрировать в CI/CD пайплайн:

```yaml
# Пример для GitHub Actions
- name: Run tests
  run: |
    pip install -r requirements-dev.txt
    pytest --cov=. --cov-report=xml

- name: Upload coverage
  uses: codecov/codecov-action@v3
```

## Советы по написанию тестов

1. **Изолируйте тесты** - каждый тест должен быть независимым
2. **Используйте фикстуры** - для повторяющихся данных
3. **Тестируйте граничные случаи** - не только happy path
4. **Проверяйте коды ответов** - убедитесь в правильном статусе
5. **Проверяйте структуру данных** - не только наличие полей
6. **Документируйте тесты** - используйте docstrings
7. **Очищайте данные** - удаляйте тестовые данные после тестов

## Известные ограничения

- Некоторые тесты используют мок-аутентификацию
- Для полноценного тестирования аутентификации нужно доработать JWT токены
- Тесты с загрузкой файлов используют фейковые файлы
- Некоторые эндпоинты требуют реальной email верификации

## Дополнительная информация

Для получения справки по pytest:

```bash
pytest --help
```

Для отладки конкретного теста:

```bash
pytest tests/test_blog.py::TestBlogEndpoints::test_get_blog_articles_default_params -v -s
```

где:
- `-v` - подробный вывод
- `-s` - показывать print() выводы
