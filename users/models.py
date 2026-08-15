from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


class UserManager(BaseUserManager):
    """Менеджер для кастомной модели пользователя"""

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email обязателен')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    """Кастомная модель пользователя с авторизацией по email"""

    username = None  # Убираем поле username

    email = models.EmailField(
        unique=True,
        verbose_name='Email'
    )
    phone = models.CharField(
        max_length=35,
        blank=True,
        null=True,
        verbose_name='Телефон'
    )
    city = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='Город'
    )
    avatar = models.ImageField(
        upload_to='avatars/',
        blank=True,
        null=True,
        verbose_name='Аватарка'
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []  # Поля, обязательные при создании суперпользователя

    objects = UserManager()  # Подключаем кастомный менеджер

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.email


class Payment(models.Model):
    """Модель платежа"""

    PAYMENT_METHODS = [
        ('cash', 'Наличные'),
        ('transfer', 'Перевод на счет'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='payments',
        verbose_name='Пользователь'
    )
    payment_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата оплаты'
    )
    paid_course = models.ForeignKey(
        'lms.Course',
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name='payments',
        verbose_name='Оплаченный курс'
    )
    paid_lesson = models.ForeignKey(
        'lms.Lesson',
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name='payments',
        verbose_name='Оплаченный урок'
    )
    amount = models.PositiveIntegerField(
        verbose_name='Сумма оплаты'
    )
    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHODS,
        default='cash',
        verbose_name='Способ оплаты'
    )

    class Meta:
        verbose_name = 'Платеж'
        verbose_name_plural = 'Платежи'
        ordering = ['-payment_date']

    def __str__(self):
        return f'{self.user.email} - {self.amount} руб.'
