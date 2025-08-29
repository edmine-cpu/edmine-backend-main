# API для перевода сообщений в чате

## Описание функциональности

Добавлена возможность перевода сообщений собеседника в чате с автоматическим определением языка исходного сообщения на целевой язык из URL.

### Особенности:

- ✅ Переводятся только сообщения собеседника (не ваши собственные)
- ✅ Автоматическое определение языка исходного сообщения
- ✅ Поддержка 5 языков: украинский (uk), английский (en), польский (pl), французский (fr), немецкий (de)
- ✅ Умная эвристика определения языка по ключевым словам
- ✅ Интеграция с существующей системой чатов

## API Endpoints

### 1. Получение сообщений с переводом

```http
GET /api/chats/{chat_id}/messages?translate_to={language}
```

**Параметры:**

- `chat_id` (path) - ID чата
- `translate_to` (query, optional) - Код языка для перевода (uk, en, pl, fr, de)
- `page` (query, optional) - Номер страницы (по умолчанию: 1)
- `limit` (query, optional) - Количество сообщений на странице (по умолчанию: 50)

**Пример запроса:**

```http
GET /api/chats/123/messages?translate_to=uk&page=1&limit=20
```

**Ответ:**

```json
{
	"messages": [
		{
			"id": 456,
			"content": "Hello, how are you?",
			"translated_content": "Привіт, як справи?",
			"detected_language": "en",
			"target_language": "uk",
			"is_translated": true,
			"sender_id": 789,
			"is_read": true,
			"created_at": "2024-01-15T10:30:00Z",
			"file_path": null,
			"file_name": null,
			"file_size": null
		}
	],
	"page": 1,
	"limit": 20,
	"has_more": false,
	"translation_enabled": true,
	"target_language": "uk",
	"supported_languages": ["uk", "en", "pl", "fr", "de"]
}
```

### 2. Массовый перевод сообщений чата

```http
POST /api/chats/{chat_id}/translate
```

**Параметры:**

- `chat_id` (path) - ID чата
- `target_language` (form) - Код языка для перевода

**Пример запроса:**

```http
POST /api/chats/123/translate
Content-Type: application/x-www-form-urlencoded

target_language=uk
```

**Ответ:**

```json
{
	"chat_id": 123,
	"target_language": "uk",
	"total_messages": 5,
	"translated_messages": [
		{
			"id": 456,
			"original_content": "Hello, how are you?",
			"translated_content": "Привіт, як справи?",
			"detected_language": "en",
			"target_language": "uk",
			"translation_available": true,
			"created_at": "2024-01-15T10:30:00Z"
		}
	]
}
```

## Поддерживаемые языки

| Код | Язык        |
| --- | ----------- |
| uk  | Украинский  |
| en  | Английский  |
| pl  | Польский    |
| fr  | Французский |
| de  | Немецкий    |

## Логика работы

### Автоматическое определение языка

Система использует эвристический подход для определения языка сообщения:

1. **Анализ ключевых слов** - проверка наличия характерных слов для каждого языка
2. **Fallback на украинский** - если язык не определен, используется украинский по умолчанию

### Примеры ключевых слов:

- **Английский**: hello, hi, good, how, what, the, and, you, are
- **Украинский**: привіт, привет, як, добре, дякую, спасибо, що, де, коли
- **Польский**: dzień, dobry, jak, się, masz, dziękuję, dzięki
- **Французский**: bonjour, comment, allez, vous, merci, au revoir
- **Немецкий**: guten, tag, wie, geht, ihnen, danke, auf wiedersehen

### Процесс перевода

1. **Проверка доступа** - пользователь должен быть участником чата
2. **Фильтрация сообщений** - переводятся только сообщения собеседника
3. **Определение языка** - автоматическое определение языка каждого сообщения
4. **Перевод** - если исходный язык отличается от целевого
5. **Ответ** - возврат оригинального и переведенного текста

## Примеры использования

### Frontend интеграция

```javascript
// Получение сообщений с переводом
const response = await fetch(`/api/chats/${chatId}/messages?translate_to=uk`)
const data = await response.json()

// Обработка переведенных сообщений
data.messages.forEach(message => {
	if (message.is_translated && message.translated_content) {
		console.log(`Оригинал: ${message.content}`)
		console.log(`Перевод: ${message.translated_content}`)
	}
})

// Массовый перевод всех сообщений
const translateResponse = await fetch(`/api/chats/${chatId}/translate`, {
	method: 'POST',
	headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
	body: `target_language=uk`,
})
```

### Кнопка translate/show original

```javascript
let isTranslationMode = false

function toggleTranslation() {
	const button = document.getElementById('translate-button')

	if (isTranslationMode) {
		// Показать оригинал
		loadMessages() // без параметра translate_to
		button.textContent = 'Translate'
		isTranslationMode = false
	} else {
		// Показать перевод
		const targetLang = getLanguageFromUrl() // получить язык из URL
		loadMessages(targetLang)
		button.textContent = 'Show Original'
		isTranslationMode = true
	}
}

function loadMessages(translateTo = null) {
	const url = translateTo
		? `/api/chats/${chatId}/messages?translate_to=${translateTo}`
		: `/api/chats/${chatId}/messages`

	fetch(url).then(/* обработка ответа */)
}
```

## Обработка ошибок

### Возможные ошибки:

- **404**: Чат не найден
- **403**: Нет доступа к чату
- **400**: Неподдерживаемый язык
- **500**: Ошибка сервиса перевода

### Пример обработки:

```javascript
try {
	const response = await fetch(`/api/chats/${chatId}/translate`, {
		method: 'POST',
		body: `target_language=${lang}`,
	})

	if (!response.ok) {
		throw new Error(`HTTP ${response.status}`)
	}

	const data = await response.json()
	// Обработка успешного ответа
} catch (error) {
	console.error('Ошибка перевода:', error)
	// Показать уведомление пользователю
}
```

---

**Примечание**: Функция перевода использует Google Translate API через библиотеку deep-translator. Для работы требуется интернет-соединение.
