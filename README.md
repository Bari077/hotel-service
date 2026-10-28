# hotel-service

Сервис для работы с отелями, интегрированный с LLM.

## Структура проекта

```
├── api/          # API эндпоинты
├── services/     # Бизнес-логика
├── llm/          # Работа с моделью и промпты
├── cache/        # Реализация кеша
├── config/       # Конфигурации (YAML/JSON)
├── tests/        # Тесты
├── main.py       # Точка входа
├── requirements.txt
└── README.md
```

## Установка

```bash
# Создание виртуального окружения
python3 -m venv venv

# Активация
source venv/bin/activate  # Linux/macOS
# venv\Scripts\activate   # Windows

# Установка зависимостей
pip install -r requirements.txt
```

## Запуск

```bash
source venv/bin/activate
python main.py
```

## Переменные окружения

Скопируйте `.env.example` в `.env` и заполните значения:

```bash
cp .env .env.local
```

Основные переменные: `APP_PORT`, `DEBUG`, `LLM_API_KEY`, `REDIS_URL`.

## Тесты

```bash
pytest
```
