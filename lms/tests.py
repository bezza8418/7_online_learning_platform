from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth.models import Group
from users.models import User
from lms.models import Course, Lesson
from lms.models import Course, Lesson, Subscription


class LessonTestCase(TestCase):
    """Тесты CRUD для уроков"""

    def setUp(self):
        """Создаём тестовые данные перед каждым тестом"""
        # Создаём пользователей
        self.user = User.objects.create_user(
            email='user@example.com',
            password='testpass123'
        )
        self.moderator = User.objects.create_user(
            email='moder@example.com',
            password='testpass123'
        )
        self.other_user = User.objects.create_user(
            email='other@example.com',
            password='testpass123'
        )

        # Создаём группу модераторов и добавляем пользователя
        self.moderator_group = Group.objects.create(name='Модераторы')
        self.moderator.groups.add(self.moderator_group)

        # Создаём курс
        self.course = Course.objects.create(
            name='Тестовый курс',
            description='Описание',
            owner=self.user
        )

        # Создаём урок
        self.lesson = Lesson.objects.create(
            name='Тестовый урок',
            description='Описание урока',
            video_link='https://www.youtube.com/watch?v=test123',
            course=self.course,
            owner=self.user
        )

        # Клиент API
        self.client = APIClient()

    def test_lesson_list_authenticated(self):
        """Авторизованный пользователь видит список уроков"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/lessons/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_lesson_list_unauthorized(self):
        """Неавторизованный пользователь не видит список уроков"""
        response = self.client.get('/api/lessons/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_lesson_create_by_user(self):
        """Обычный пользователь может создать урок"""
        self.client.force_authenticate(user=self.user)
        data = {
            'name': 'Новый урок',
            'description': 'Описание',
            'video_link': 'https://www.youtube.com/watch?v=new123',
            'course': self.course.id
        }
        response = self.client.post('/api/lessons/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['owner'], self.user.id)

    def test_lesson_create_by_moderator(self):
        """Модератор НЕ может создать урок"""
        self.client.force_authenticate(user=self.moderator)
        data = {
            'name': 'Новый урок',
            'description': 'Описание',
            'video_link': 'https://www.youtube.com/watch?v=new123',
            'course': self.course.id
        }
        response = self.client.post('/api/lessons/', data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_lesson_retrieve(self):
        """Получение одного урока"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(f'/api/lessons/{self.lesson.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Тестовый урок')

    def test_lesson_update_by_owner(self):
        """Владелец может обновить свой урок"""
        self.client.force_authenticate(user=self.user)
        data = {'name': 'Обновлённый урок'}
        response = self.client.patch(f'/api/lessons/{self.lesson.id}/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_lesson_update_by_other_user(self):
        """Другой пользователь НЕ может обновить чужой урок"""
        self.client.force_authenticate(user=self.other_user)
        data = {'name': 'Обновлённый урок'}
        response = self.client.patch(f'/api/lessons/{self.lesson.id}/', data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_lesson_update_by_moderator(self):
        """Модератор может обновить любой урок"""
        self.client.force_authenticate(user=self.moderator)
        data = {'name': 'Обновлено модератором'}
        response = self.client.patch(f'/api/lessons/{self.lesson.id}/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_lesson_delete_by_owner(self):
        """Владелец может удалить свой урок"""
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(f'/api/lessons/{self.lesson.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_lesson_delete_by_other_user(self):
        """Другой пользователь НЕ может удалить чужой урок"""
        self.client.force_authenticate(user=self.other_user)
        response = self.client.delete(f'/api/lessons/{self.lesson.id}/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_lesson_delete_by_moderator(self):
        """Модератор НЕ может удалить урок"""
        self.client.force_authenticate(user=self.moderator)
        response = self.client.delete(f'/api/lessons/{self.lesson.id}/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_lesson_invalid_video_link(self):
        """Создание урока с невалидной ссылкой возвращает ошибку"""
        self.client.force_authenticate(user=self.user)
        data = {
            'name': 'Новый урок',
            'description': 'Описание',
            'video_link': 'https://www.stepik.org/course/123',
            'course': self.course.id
        }
        response = self.client.post('/api/lessons/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_lesson_delete_by_owner(self):
        """Владелец может удалить свой урок"""
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(f'/api/lessons/{self.lesson.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


class SubscriptionTestCase(TestCase):
    """Тесты для подписки на курс"""

    def setUp(self):
        """Создаём тестовые данные"""
        self.user = User.objects.create_user(
            email='sub_user@example.com',
            password='testpass123'
        )
        self.other_user = User.objects.create_user(
            email='sub_other@example.com',
            password='testpass123'
        )
        self.course = Course.objects.create(
            name='Курс для подписки',
            description='Описание',
            owner=self.user
        )
        self.client = APIClient()

    def test_subscribe_authorized(self):
        """Авторизованный пользователь может подписаться на курс"""
        self.client.force_authenticate(user=self.user)
        response = self.client.post('/api/subscribe/', {'course_id': self.course.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'подписка добавлена')
        self.assertTrue(
            Subscription.objects.filter(user=self.user, course=self.course).exists()
        )

    def test_unsubscribe(self):
        """Повторный запрос удаляет подписку"""
        self.client.force_authenticate(user=self.user)
        # Сначала подписываемся
        self.client.post('/api/subscribe/', {'course_id': self.course.id})
        # Потом отписываемся
        response = self.client.post('/api/subscribe/', {'course_id': self.course.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'подписка удалена')
        self.assertFalse(
            Subscription.objects.filter(user=self.user, course=self.course).exists()
        )

    def test_subscribe_unauthorized(self):
        """Неавторизованный пользователь не может подписаться"""
        response = self.client.post('/api/subscribe/', {'course_id': self.course.id})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_subscribe_course_not_found(self):
        """Подписка на несуществующий курс возвращает 404"""
        self.client.force_authenticate(user=self.user)
        response = self.client.post('/api/subscribe/', {'course_id': 99999})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_is_subscribed_field_in_course(self):
        """В сериализаторе курса отображается признак подписки"""
        self.client.force_authenticate(user=self.user)
        # Подписываемся
        self.client.post('/api/subscribe/', {'course_id': self.course.id})
        # Проверяем поле is_subscribed
        response = self.client.get(f'/api/courses/{self.course.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['is_subscribed'])

    def test_is_subscribed_false_for_other_user(self):
        """Для другого пользователя is_subscribed = False"""
        # Подписываем первого пользователя
        self.client.force_authenticate(user=self.user)
        self.client.post('/api/subscribe/', {'course_id': self.course.id})
        # Проверяем от лица другого пользователя
        self.client.force_authenticate(user=self.other_user)
        response = self.client.get(f'/api/courses/{self.course.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['is_subscribed'])


class CourseTestCase(TestCase):
    """Тесты CRUD для курсов"""

    def setUp(self):
        self.user = User.objects.create_user(
            email='course_user@example.com',
            password='testpass123'
        )
        self.moderator = User.objects.create_user(
            email='course_moder@example.com',
            password='testpass123'
        )
        self.other_user = User.objects.create_user(
            email='course_other@example.com',
            password='testpass123'
        )
        self.moderator_group = Group.objects.create(name='Модераторы')
        self.moderator.groups.add(self.moderator_group)

        self.course = Course.objects.create(
            name='Тестовый курс',
            description='Описание',
            owner=self.user
        )
        self.client = APIClient()

    def test_course_list_authenticated(self):
        """Авторизованный пользователь видит список курсов"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/courses/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_course_list_unauthorized(self):
        """Неавторизованный пользователь не видит список курсов"""
        response = self.client.get('/api/courses/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_course_create_by_user(self):
        """Обычный пользователь может создать курс"""
        self.client.force_authenticate(user=self.user)
        data = {'name': 'Новый курс', 'description': 'Описание'}
        response = self.client.post('/api/courses/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['owner'], self.user.id)

    def test_course_create_by_moderator(self):
        """Модератор НЕ может создать курс"""
        self.client.force_authenticate(user=self.moderator)
        data = {'name': 'Новый курс', 'description': 'Описание'}
        response = self.client.post('/api/courses/', data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_course_retrieve(self):
        """Получение одного курса"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(f'/api/courses/{self.course.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_course_update_by_owner(self):
        """Владелец может обновить свой курс"""
        self.client.force_authenticate(user=self.user)
        response = self.client.patch(f'/api/courses/{self.course.id}/', {'name': 'Обновлён'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_course_update_by_other_user(self):
        """Другой пользователь НЕ может обновить чужой курс"""
        self.client.force_authenticate(user=self.other_user)
        response = self.client.patch(f'/api/courses/{self.course.id}/', {'name': 'Обновлён'})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_course_update_by_moderator(self):
        """Модератор может обновить любой курс"""
        self.client.force_authenticate(user=self.moderator)
        response = self.client.patch(f'/api/courses/{self.course.id}/', {'name': 'Обновлён модером'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_course_delete_by_owner(self):
        """Владелец может удалить свой курс"""
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(f'/api/courses/{self.course.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_course_delete_by_moderator(self):
        """Модератор НЕ может удалить курс"""
        self.client.force_authenticate(user=self.moderator)
        response = self.client.delete(f'/api/courses/{self.course.id}/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
