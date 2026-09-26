from django.core.management.base import BaseCommand
from users.models import User, Payment
from lms.models import Course, Lesson
from random import choice, randint


class Command(BaseCommand):
    help = 'Заполняет таблицу Payment тестовыми данными'

    def handle(self, *args, **options):
        users = User.objects.all()
        courses = Course.objects.all()
        lessons = Lesson.objects.all()
        methods = ['cash', 'transfer']

        if not users.exists():
            self.stdout.write('Нет пользователей. Сначала создайте пользователей.')
            return

        for _ in range(10):
            Payment.objects.create(
                user=choice(users),
                paid_course=choice(courses) if courses.exists() else None,
                paid_lesson=choice(lessons) if lessons.exists() else None,
                amount=randint(100, 10000),
                payment_method=choice(methods)
            )

        self.stdout.write('Тестовые платежи созданы успешно!')
