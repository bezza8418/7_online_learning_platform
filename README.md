# 7_online_learning_platform

Платформа для онлайн-обучения (LMS) на Django REST Framework.

---

## Быстрый старт через Docker

1. Создайте `.env` по примеру `.env.example`
2. Запустите:
   docker-compose up --build
3. Приложение доступно:
   - API: http://localhost:8000/api/
   - Админка: http://localhost:8000/admin/
   - Swagger: http://localhost:8000/api/docs/
   - ReDoc: http://localhost:8000/api/redoc/
4. Создайте суперпользователя:
   docker-compose exec web python manage.py createsuperuser
5. Остановка:
   docker-compose down
---

## Локальный запуск

1. Установите зависимости:
   pip install -r requirements.txt
2. Примените миграции:
   python manage.py migrate
3. Запустите сервер:
   python manage.py runserver
---

## Переменные окружения

Создайте `.env` по примеру `.env.example`:

```env
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,web

DB_NAME=online_learning_db
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=db
DB_PORT=5432

REDIS_HOST=redis
REDIS_PORT=6379
REDIS_DB=0
```

## Документация API
Полная документация всех эндпоинтов — в Swagger:

http://localhost:8000/api/docs/

## Тесты
python manage.py test

## Автор
bezza8418