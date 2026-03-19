# Movie API

Профессиональная система управления фильмами с REST API, мягким удалением и полной документацией.

## Технологический стек
* **Backend:** Python 3.12 + Django 6.0.3
* **Database:** PostgreSQL 16
* **ORM:** Django ORM (встроенный) с кастомными менеджерами
* **API Framework:** Django REST Framework 3.16.1
* **DevOps:** Docker & Docker Compose
* **Validation:** DRF Serializers с кастомной валидацией

## Ключевые особенности
* **Soft Delete (Мягкое удаление):** Фильмы не удаляются физически из базы данных, а помечаются временной меткой `deleted_at`. Это позволяет сохранять историю и восстанавливать данные при необходимости.
* **Кастомные менеджеры:** Два менеджера модели - `objects` (все записи) и `active_objects` (только неудаленные) для удобной работы с данными.
* **Автоматические временные метки:** Поля `created_at` и `updated_at` обновляются автоматически при создании и изменении записей.
* **Smart Pagination:** Список фильмов возвращается с мета-данными (общее кол-во, текущая страница, лимит, всего страниц).
* **Docker-first:** Полная изоляция среды. Проект гарантированно запускается на Windows, macOS и Linux.

## Быстрый старт

### 1. Запуск инфраструктуры
```powershell
docker-compose up -d --build
```

### 2. Применение миграций
```powershell
docker-compose exec app python manage.py migrate
```

### 3. Документация
**Веб-интерфейс:** http://localhost:4200/ - главная страница со списком фильмов и документацией

**API Endpoints:**
- `GET /api/movies/` - список всех активных фильмов (с пагинацией)
- `GET /api/movies/{id}/` - получить фильм по ID
- `POST /api/movies/` - создать новый фильм
- `PUT /api/movies/{id}/` - полностью обновить фильм
- `PATCH /api/movies/{id}/` - частично обновить фильм
- `DELETE /api/movies/{id}/` - мягкое удаление фильма

### 4. Реализация Soft Delete
Команды для просмотра "мягко" удаленных фильмов через Django ORM:

```powershell
docker-compose exec app python manage.py shell -c "from movies.models import Movie; print([(m.id, m.title, m.year, 'DELETED' if m.deleted_at else 'ACTIVE') for m in Movie.objects.all()])"
```

### 5. Формат ответа API (пагинация)
```json
{
    "data": [
        {
            "id": 1,
            "title": "Начало",
            "director": "Кристофер Нолан",
            "year": 2010,
            "created_at": "2026-03-19T18:44:03.123456Z",
            "updated_at": "2026-03-19T18:44:03.123456Z"
        }
    ],
    "meta": {
        "total": 12,
        "page": 1,
        "limit": 10,
        "totalPages": 2
    }
}
```

## Примеры данных для тестирования (POST /api/movies/)

```json
{
  "title": "Бойцовский клуб",
  "director": "Дэвид Финчер",
  "year": 1999
}
```

```json
{
  "title": "Джентльмены",
  "director": "Гай Ричи",
  "year": 2019
}
```

```json
{
  "title": "Остров проклятых",
  "director": "Мартин Скорсезе",
  "year": 2010
}
```

## Структура проекта
```
lab2/
├── docker-compose.yml          # Конфигурация Docker
├── Dockerfile                   # Сборка образа приложения
├── requirements.txt             # Зависимости Python
├── manage.py                    # Управление Django проектом
├── .env                         # Переменные окружения
├── backup.sql                   # Резервная копия базы данных
├── movies/                      # Приложение movies
│   ├── models.py                 # Модель Movie с soft delete
│   ├── views.py                   # Представления (API и HTML)
│   ├── serializers.py             # DRF сериализаторы с валидацией
│   ├── services.py                 # Сервисный слой
│   ├── urls.py                     # Маршруты приложения
│   ├── apps.py                      # Конфигурация приложения
│   └── templates/                   # HTML шаблоны
│       └── movies/
│           └── index.html              # Главная страница
└── lab2/                         # Основная конфигурация проекта
    ├── settings.py                 # Настройки Django
    ├── urls.py                       # Главные маршруты
    ├── asgi.py                        # ASGI конфигурация
    └── wsgi.py                        # WSGI конфигурация
```

## Валидация данных

### POST /api/movies/ (создание)
- **year**: от 1888 до текущий год + 5
- **title**: минимум 2 символа, не пустой
- **director**: обязательное поле

### PUT /api/movies/{id}/ (полное обновление)
- Все поля обязательны
- Те же правила валидации что и при создании

### PATCH /api/movies/{id}/ (частичное обновление)
- Любое поле опционально
- Указанные поля проходят валидацию

## Обработка ошибок
- **400 Bad Request**: Неверный формат данных или ошибка валидации
- **404 Not Found**: Фильм не найден или был удален
- **500 Internal Server Error**: Внутренняя ошибка сервера
