# 7_online_learning_platform

Платформа для онлайн-обучения (LMS) на Django REST Framework.

---

## Приложение доступно

- **API**: http://111.88.157.129/api/
- **Swagger**: http://111.88.157.129/api/docs/
- **ReDoc**: http://111.88.157.129/api/redoc/
- **Админка**: http://111.88.157.129/admin/

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


## Деплой

Проект автоматически деплоится на сервер через **GitHub Actions**.

### Как это работает

1. Push в ветку `develop`
2. GitHub Actions запускает:
   - **test** — тесты
   - **lint** — flake8
   - **deploy** — деплой на сервер по SSH
3. Если все этапы успешны — проект обновляется на сервере

### Сервер

- **IP**: ваш IP
- **Проект**: `/var/www/7_online_learning_platform`
- **Запуск**: `docker compose up -d --build`

### Секреты GitHub

Для деплоя нужны секреты в GitHub:
- `SERVER_IP` — IP сервера
- `SERVER_USER` — пользователь
- `SSH_PRIVATE_KEY` — приватный SSH-ключ

### Ручной деплой
```
ssh -i ~/.ssh/github_deploy user@server_ip
cd /var/www/7_online_learning_platform
git pull origin develop
sudo docker compose down
sudo docker compose up -d --build
```

## Тесты
python manage.py test

## Автор
bezza8418