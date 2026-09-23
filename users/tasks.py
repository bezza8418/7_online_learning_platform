from celery import shared_task
from django.utils import timezone
from datetime import timedelta


@shared_task
def block_inactive_users():
    """
    Блокирует пользователей, которые не заходили более месяца.

    Обновление происходит батчем (одним запросом), а не по одному.
    """
    from users.models import User

    one_month_ago = timezone.now() - timedelta(days=30)

    # Батчевое обновление: одним запросом
    updated_count = User.objects.filter(
        last_login__lt=one_month_ago,
        is_active=True
    ).update(is_active=False)

    # Также блокируем тех, кто ни разу не заходил (last_login = None)
    # и был создан более месяца назад
    updated_count += User.objects.filter(
        last_login__isnull=True,
        date_joined__lt=one_month_ago,
        is_active=True
    ).update(is_active=False)

    return f'Заблокировано пользователей: {updated_count}'
