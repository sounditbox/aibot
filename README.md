# AIBot - AI-генератор постов для Telegram

Автоматический парсинг новостей, генерация постов через OpenAI и публикация в Telegram.

## Быстрый старт

1. **Настройка окружения:**
```bash
cp .env.example .env
# Заполните TELERGAM_API_ID, TELERGAM_API_HASH, OPENAI_API_KEY
```

2. **Запуск:**
```bash
docker-compose up -d
```

3. **Авторизация Telegram:**
```bash
# Через API
curl -X POST http://localhost:8000/api/telegram/authorize/ \
  -H "Content-Type: application/json" \
  -d '{"phone": "+79991234567"}'

# Или через скрипт
python -m app.telegram.auth
```

4. **API документация:**
http://localhost:8000/docs

## Основные endpoints

- `GET /api/sources/` - список источников
- `POST /api/sources/` - добавить источник
- `GET /api/posts/` - список постов
- `POST /api/parse-sources/` - запустить парсинг
- `POST /api/publish-posts/` - запустить публикацию
- `POST /api/telegram/authorize/` - авторизация Telegram

## Структура

- `app/tasks.py` - Celery задачи (парсинг, генерация, публикация)
- `app/api/` - REST API endpoints
- `app/telegram/` - интеграция с Telegram
- `app/news_parser/` - парсеры новостей

## Переменные окружения

```env
TELERGAM_API_ID=your_api_id
TELERGAM_API_HASH=your_api_hash
TELERGAM_CHANNEL_USERNAME=your_channel
OPENAI_API_KEY=your_key
DATABASE_URL=postgresql+psycopg://postgres:postgres@postgres:5432/aibot
```
