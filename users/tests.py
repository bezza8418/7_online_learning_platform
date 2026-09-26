from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from users.models import User


class UserRegistrationTestCase(TestCase):
    """Тесты регистрации пользователей"""

    def setUp(self):
        self.client = APIClient()

    def test_register_user(self):
        """Успешная регистрация"""
        data = {
            'email': 'newuser@example.com',
            'password': 'testpass123',
            'password_confirm': 'testpass123',
            'first_name': 'Иван',
            'last_name': 'Иванов'
        }
        response = self.client.post('/api/register/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(email='newuser@example.com').exists())

    def test_register_duplicate_email(self):
        """Регистрация с существующим email возвращает ошибку"""
        User.objects.create_user(email='existing@example.com', password='testpass123')
        data = {
            'email': 'existing@example.com',
            'password': 'testpass123',
            'password_confirm': 'testpass123'
        }
        response = self.client.post('/api/register/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_password_mismatch(self):
        """Несовпадение паролей возвращает ошибку"""
        data = {
            'email': 'newuser2@example.com',
            'password': 'testpass123',
            'password_confirm': 'different'
        }
        response = self.client.post('/api/register/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class UserCRUDTestCase(TestCase):
    """Тесты CRUD для пользователей"""

    def setUp(self):
        self.user = User.objects.create_user(
            email='user1@example.com',
            password='testpass123',
            first_name='Иван',
            last_name='Иванов'
        )
        self.other_user = User.objects.create_user(
            email='user2@example.com',
            password='testpass123'
        )
        self.client = APIClient()

    def test_user_list_authenticated(self):
        """Авторизованный видит список пользователей"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/users/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_list_unauthorized(self):
        """Неавторизованный не видит список"""
        response = self.client.get('/api/users/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_retrieve_own_profile(self):
        """Пользователь видит свой полный профиль"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(f'/api/users/{self.user.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('last_name', response.data)

    def test_user_retrieve_other_profile(self):
        """Чужой профиль — только общая информация"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(f'/api/users/{self.other_user.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotIn('last_name', response.data)

    def test_user_update_own_profile(self):
        """Пользователь может обновить свой профиль"""
        self.client.force_authenticate(user=self.user)
        response = self.client.patch(f'/api/users/{self.user.id}/', {'first_name': 'Пётр'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_update_other_profile(self):
        """Пользователь НЕ может обновить чужой профиль"""
        self.client.force_authenticate(user=self.user)
        response = self.client.patch(f'/api/users/{self.other_user.id}/', {'first_name': 'Пётр'})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
