# hotel-service

Сервис для работы с отелями, интегрированный с LLM.

## Структура проекта

```
├── api/          # API эндпоинты, схемы, представления
│   ├── routes.py
│   ├── schemas.py
│   └── views.py
├── cache/        # Redis кеш
│   └── cache.py
├── llm/          # LLM клиент, промпты, Pydantic-схемы
│   ├── model.py
│   ├── prompts.py
│   └── schemas.py
├── services/     # Бизнес-логика
│   └── service.py
├── templates/    # Веб-интерфейс
│   └── index.html
├── tests/        # Тесты
│   ├── test_api.py
│   ├── test_cache.py
│   ├── test_llm.py
│   └── test_services.py
├── utils/        # Утилиты
│   └── logging.py
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
cp .env.example .env
```

Основные переменные: `APP_PORT`, `DEBUG`, `LLM_AUTH_KEY`, `REDIS_URL`, `CACHE_TTL`.

## Примеры запросов и ответов

### Запрос

```bash
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Подскажи отели в Турции, Анталья, 5 звезд, первая береговая"
  }'
```

### Ответ (успешный)

```json
{
  "message": {
    "hotelList": [
      {
        "region": "Анталья",
        "hotels": [
          {
            "hotel": "Rixos Premium Sungate",
            "category": 5,
            "description": "Роскошный курорт с прямым выходом к пляжу и собственным аквапарком.",
            "advantages": "Прямой выход к морю, семейный отдых, все включено, детские клубы",
            "nuance": "Высокие цены в пиковый сезон, рекомендуется бронировать заранее"
          },
          {
            "hotel": "Titanium De Luxe Resort",
            "category": 5,
            "description": "Современный курорт с панорамным бассейном и видом на Средиземное море.",
            "advantages": "Первая береговая линия, спа-центр, европейская кухня",
            "nuance": "Расположен вдали от центра города, требуется трансфер"
          }
        ]
      }
    ],
    "travelRecommendation": "Лучшее время для отдыха в Турции — май-октябрь. В это время комфортная погода и теплое море."
  },
  "status": "ok"
}
```

### Ответ (ошибка валидации)

```json
{
  "error": "Сообщение не может состоять только из пробелов",
  "status": 422
}
```

### Ответ (сервис недоступен)

```json
{
  "error": "Модель вернула некорректный ответ. Попробуйте переформулировать запрос",
  "status": 500
}
```

## Тесты

```bash
pytest
```
