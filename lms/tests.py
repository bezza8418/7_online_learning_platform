from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth.models import Group
from users.models import User
from lms.models import Course, Lesson


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
