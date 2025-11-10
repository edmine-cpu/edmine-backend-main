# API Документация для фронтенда

## Управление заявками пользователя

### 1. Получить список своих заявок

**GET** `/my-bids`

Получить все заявки текущего авторизованного пользователя.

#### Параметры запроса
- `limit` (optional, integer): Количество заявок для возврата. Максимум 100, по умолчанию 20.

#### Заголовки
```
Authorization: Bearer {jwt_token}
```
или JWT токен в cookie `jwt_token`

#### Пример запроса
```javascript
fetch('/my-bids?limit=50', {
  method: 'GET',
  headers: {
    'Authorization': 'Bearer YOUR_JWT_TOKEN'
  }
})
```

#### Ответ
```json
[
  {
    "id": 123,
    "title_uk": "Потрібен веб-розробник",
    "title_en": "Need web developer",
    "description_uk": "Опис проекту...",
    "description_en": "Project description...",
    "budget": 5000,
    "budget_type": "fixed",
    "country": { "id": 1, "name_en": "Ukraine" },
    "city": { "id": 10, "name_en": "Kyiv" },
    "categories": [1, 5],
    "under_categories": [12, 15],
    "files": ["/static/files/file1.pdf"],
    "created_at": "2025-01-10T10:00:00",
    "updated_at": "2025-01-10T10:00:00"
  }
]
```

---

### 2. Обновить свою заявку

**PUT** `/my-bids/{bid_id}`

Обновить существующую заявку пользователя. Пользователь может обновлять только свои собственные заявки.

#### Параметры URL
- `bid_id` (required, integer): ID заявки для обновления

#### Заголовки
```
Authorization: Bearer {jwt_token}
Content-Type: multipart/form-data
```

#### Тело запроса (Form Data)

Все поля опциональные. Отправляйте только те поля, которые нужно обновить:

| Поле | Тип | Описание |
|------|-----|----------|
| `title_uk` | string | Заголовок на украинском |
| `title_en` | string | Заголовок на английском |
| `title_pl` | string | Заголовок на польском |
| `title_fr` | string | Заголовок на французском |
| `title_de` | string | Заголовок на немецком |
| `description_uk` | string | Описание на украинском |
| `description_en` | string | Описание на английском |
| `description_pl` | string | Описание на польском |
| `description_fr` | string | Описание на французском |
| `description_de` | string | Описание на немецком |
| `country` | integer | ID страны |
| `city` | integer | ID города |
| `budget` | integer | Бюджет проекта |
| `budget_type` | string | Тип бюджета ("fixed", "hourly", etc.) |
| `category` | string/array | ID категорий (через запятую: "1,5,8" или массив) |
| `under_category` | string/array | ID подкатегорий (через запятую: "12,15" или массив) |

#### Пример запроса (JavaScript)
```javascript
const formData = new FormData();
formData.append('title_uk', 'Оновлений заголовок');
formData.append('title_en', 'Updated title');
formData.append('description_uk', 'Оновлений опис проекту');
formData.append('budget', '6000');
formData.append('category', '1,5,8');
formData.append('under_category', '12,15');

fetch('/my-bids/123', {
  method: 'PUT',
  headers: {
    'Authorization': 'Bearer YOUR_JWT_TOKEN'
  },
  body: formData
})
```

#### Ответ успеха
```json
{
  "success": true,
  "message": "Заявка успешно обновлена"
}
```

#### Ошибки
- **401 Unauthorized**: Пользователь не авторизован
- **403 Forbidden**: Попытка редактировать чужую заявку
- **404 Not Found**: Заявка не найдена

```json
{
  "detail": "Нет прав для редактирования этой заявки"
}
```

#### Особенности
- **Автоматический перевод**: Если вы заполните только одно языковое поле (например, `title_uk`), система автоматически переведет его на остальные языки
- **Автоматическое обновление slug**: При изменении заголовков автоматически обновляются URL-slug'и для всех языков
- **Проверка прав**: Пользователь может редактировать только свои заявки

---

### 3. Удалить свою заявку

**DELETE** `/my-bids/{bid_id}`

Удалить существующую заявку пользователя. Пользователь может удалять только свои собственные заявки.

#### Параметры URL
- `bid_id` (required, integer): ID заявки для удаления

#### Заголовки
```
Authorization: Bearer {jwt_token}
```

#### Пример запроса
```javascript
fetch('/my-bids/123', {
  method: 'DELETE',
  headers: {
    'Authorization': 'Bearer YOUR_JWT_TOKEN'
  }
})
```

#### Ответ успеха
```json
{
  "success": true,
  "message": "Заявка успешно удалена"
}
```

#### Ошибки
- **401 Unauthorized**: Пользователь не авторизован
- **403 Forbidden**: Попытка удалить чужую заявку
- **404 Not Found**: Заявка не найдена

```json
{
  "detail": "Нет прав для удаления этой заявки"
}
```

#### Особенности
- **Автоматическое удаление файлов**: При удалении заявки автоматически удаляются все прикрепленные файлы
- **Проверка прав**: Пользователь может удалять только свои заявки
- **Безвозвратное удаление**: Восстановление удаленной заявки невозможно

---

## Профиль пользователя (обновлено)

### Изменения в API профиля

⚠️ **ВАЖНО**: Поля `country` и `city` были **удалены** из модели пользователя. Эти поля теперь существуют только для заявок (Bid) и компаний (Company).

### GET `/profile`

Получить профиль текущего пользователя.

#### Обновленный ответ (убраны country и city)
```json
{
  "id": 1,
  "name": "Иван Иванов",
  "nickname": "ivan_dev",
  "email": "ivan@example.com",
  "avatar": "/static/avatars/abc123.jpg",
  "user_role": "customer",
  "profile_description": "Опытный заказчик проектов",
  "language": "uk",
  "categories": [
    {
      "id": 1,
      "name_uk": "Розробка",
      "name_en": "Development",
      "name_pl": "Rozwój",
      "name_fr": "Développement",
      "name_de": "Entwicklung"
    }
  ],
  "subcategories": [
    {
      "id": 12,
      "name_uk": "Веб-розробка",
      "name_en": "Web Development",
      "name_pl": "Rozwój stron internetowych",
      "name_fr": "Développement web",
      "name_de": "Webentwicklung"
    }
  ]
}
```

### Удаленные эндпоинты

Следующий эндпоинт был **удален**:
- ~~`PUT /profile/location`~~ - больше не существует

### Доступные эндпоинты профиля

1. **PUT** `/profile/nickname` - Обновить никнейм
2. **PUT** `/profile/name` - Обновить имя
3. **PUT** `/profile/description` - Обновить описание профиля
4. **PUT** `/profile/role` - Обновить роль (customer/contractor)
5. **PUT** `/profile/avatar` - Загрузить аватар
6. **DELETE** `/profile/avatar` - Удалить аватар
7. **PUT** `/profile/categories` - Обновить категории и подкатегории
8. **PUT** `/profile/multilang` - Обновить мультиязычную информацию о компании

---

## Общие примечания

### Авторизация
Все эндпоинты для управления заявками требуют авторизации. Используйте один из способов:
1. JWT токен в заголовке: `Authorization: Bearer YOUR_JWT_TOKEN`
2. JWT токен в cookie с именем `jwt_token`

### Обработка ошибок
Все ошибки возвращаются в формате:
```json
{
  "detail": "Описание ошибки"
}
```

Коды ошибок:
- `400` - Неверные параметры запроса
- `401` - Не авторизован
- `403` - Нет прав доступа
- `404` - Ресурс не найден
- `500` - Внутренняя ошибка сервера

### Мультиязычность
Система поддерживает 5 языков:
- `uk` - украинский
- `en` - английский
- `pl` - польский
- `fr` - французский
- `de` - немецкий

При создании или обновлении заявок можно заполнить поля только на одном языке, система автоматически переведет на остальные языки.

### Лимиты
- Максимальное количество заявок в одном запросе: 100
- Максимальный размер файла для аватара: 5 MB
- Поддерживаемые форматы изображений: JPG, PNG, GIF, WEBP
