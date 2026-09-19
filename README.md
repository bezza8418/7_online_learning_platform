# 7_online_learning_platform

Платформа для онлайн-обучения (LMS). Реализована на Django REST Framework.

---

## Технологии

- Python 3.12+
- Django 5.x
- Django REST Framework
- PostgreSQL
- Pillow (для работы с изображениями)
- python-dotenv

## Установка и запуск
```
1. Клонируйте репозиторий:

   git clone https://github.com/ваш_ник/7_online_learning_platform.git
   cd 7_online_learning_platform

2. Создайте виртуальное окружение и активируйте его:

   python -m venv venv
   source venv/bin/activate  # для Linux/Mac
   venv\Scripts\activate     # для Windows

3. Установите зависимости:

   pip install -r requirements.txt

4. Создайте файл .env и заполните его по примеру .env.example:

   DB_NAME=your_db_name
   DB_USER=your_db_user
   DB_PASSWORD=your_db_password
   DB_HOST=localhost
   DB_PORT=5432

   SECRET_KEY=your-secret-key
   DEBUG=True
   ALLOWED_HOSTS=localhost,127.0.0.1

5. Создайте базу данных PostgreSQL:

   CREATE DATABASE your_db_name;

6. Примените миграции:

   python manage.py migrate

7. Создайте суперпользователя:

   python manage.py createsuperuser

8. Запустите сервер:

   python manage.py runserver
```

## API Эндпоинты

### Курсы (ViewSet)

| Метод | URL | Описание |
|-------|-----|----------|
| GET | /api/courses/ | Список курсов |
| POST | /api/courses/ | Создать курс |
| GET | /api/courses/{id}/ | Получить курс |
| PUT | /api/courses/{id}/ | Обновить курс |
| PATCH | /api/courses/{id}/ | Частично обновить курс |
| DELETE | /api/courses/{id}/ | Удалить курс |

### Уроки (Generic-классы)

| Метод | URL | Описание |
|-------|-----|----------|
| GET | /api/lessons/ | Список уроков |
| POST | /api/lessons/ | Создать урок |
| GET | /api/lessons/{id}/ | Получить урок |
| PUT | /api/lessons/{id}/ | Обновить урок |
| PATCH | /api/lessons/{id}/ | Частично обновить урок |
| DELETE | /api/lessons/{id}/ | Удалить урок |

### Пользователи

| Метод | URL | Описание |
|-------|-----|----------|
| GET | /api/users/ | Список пользователей |
| POST | /api/users/ | Создать пользователя |
| GET | /api/users/{id}/ | Получить пользователя |
| PUT | /api/users/{id}/ | Обновить пользователя |
| PATCH | /api/users/{id}/ | Частично обновить пользователя |
| DELETE | /api/users/{id}/ | Удалить пользователя |

### Админка

- /admin/ — стандартная админка Django

---

## Модели

### User (кастомная модель)

- Авторизация по email (USERNAME_FIELD = 'email')
- Поля: email, phone, city, avatar

### Course

- name — название курса
- preview — превью (картинка)
- description — описание

### Lesson

- name — название урока
- description — описание
- preview — превью (картинка)
- video_link — ссылка на видео
- Связь с Course (ForeignKey)

---

## Проверка в Postman

Все эндпоинты доступны по адресу: http://127.0.0.1:8000/api/

Пример запроса на создание курса:

{
    "name": "Python для начинающих",
    "preview": null,
    "description": "Базовый курс по Python"
}

Пример запроса на создание урока:

{
    "name": "Урок 1: Введение",
    "description": "Первое знакомство с Python",
    "preview": null,
    "video_link": "https://www.youtube.com/watch?v=example",
    "course": 1
}

---

# Аутентификация

Проект использует JWT-авторизацию.

### Получение токенов

POST /api/token/
{
    "email": "user@example.com",
    "password": "password"
}

Ответ:
{
    "refresh": "...",
    "access": "..."
}

### Обновление токена

POST /api/token/refresh/
{
    "refresh": "..."
}

### Использование токена

В каждом запросе передавайте заголовок:
Authorization: Bearer <access_token>

---

## Регистрация

```
POST /api/register/
{
    "email": "user@example.com",
    "password": "password123",
    "password_confirm": "password123",
    "first_name": "Иван",
    "last_name": "Иванов",
    "phone": "+79991234567",
    "city": "Москва"
}
```

---

## Права доступа

### Группа "Модераторы"

- ✅ Просмотр любых курсов и уроков
- ✅ Редактирование любых курсов и уроков
- ❌ Создание курсов и уроков
- ❌ Удаление курсов и уроков

### Обычные пользователи

- ✅ Просмотр всех курсов и уроков
- ✅ Создание курсов и уроков
- ✅ Редактирование **только своих** курсов и уроков
- ✅ Удаление **только своих** курсов и уроков

### Профиль пользователя

- ✅ Просмотр любого профиля (только общая информация)
- ✅ Редактирование **только своего** профиля

---

## Фикстуры

Для загрузки групп модераторов:
```
python manage.py loaddata users/fixtures/groups.json
```

---

## Тестовые данные

Для заполнения платежей:
```
python manage.py fill_payments
```

## Валидация

Ссылки на видео в уроках проходят валидацию по домену:
- Разрешены: `youtube.com`, `youtu.be` и их поддомены
- Похожие адреса (`fake-youtube.com`, `notyoutube.com.evil.com`) — отклоняются

## Подписка на курсы

### Управление подпиской

POST /api/subscribe/
{
    "course_id": 1
}

Ответ:
{
    "message": "подписка добавлена"  // или "подписка удалена"
}

### Признак подписки

В сериализаторе курса есть поле `is_subscribed`:
- `true` — текущий пользователь подписан на курс
- `false` — не подписан

## Пагинация

Для курсов и уроков настроена пагинация:

- `?page=1` — номер страницы
- `?page_size=10` — количество элементов на странице (макс. 50)

Пример:
GET /api/courses/?page=2&page_size=3

### Модераторы
- Видят все курсы и уроки
- Могут редактировать любые курсы и уроки
- **Не могут** создавать и удалять

### Обычные пользователи
- Видят **только свои** курсы и уроки
- Могут создавать курсы и уроки
- Могут редактировать и удалять **только свои** объекты
- При попытке получить чужой объект — **404** (не 403, чтобы не раскрывать существование)

## Тесты

Проект покрыт тестами (38 тестов):

python manage.py test

### Покрытие тестами

coverage run --source='.' manage.py test
coverage report

Отчёт покрытия — в файле `coverage.txt`.


## 📄 Лицензия
Проект разработан в учебных целях.

## 📞 Контакты
Автор: bezza8418