from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings


@shared_task
def send_course_update_email(course_id):
    """
    Отправляет письмо всем подписчикам курса об обновлении материалов.

    :param course_id: ID курса, который был обновлён
    """
    from lms.models import Course, Subscription

    try:
        course = Course.objects.get(id=course_id)
    except Course.DoesNotExist:
        return f'Курс с id={course_id} не найден'

    subscriptions = Subscription.objects.filter(course=course).select_related('user')

    if not subscriptions.exists():
        return f'У курса "{course.name}" нет подписчиков'

    emails = [sub.user.email for sub in subscriptions if sub.user.email]

    if not emails:
        return 'Нет email-адресов для отправки'

    send_mail(
        subject=f'Обновление курса: {course.name}',
        message=(
            f'Здравствуйте!\n\n'
            f'Курс "{course.name}" был обновлён.\n'
            f'Проверьте новые материалы в личном кабинете.\n\n'
            f'С уважением,\n'
            f'Команда Online Learning Platform'
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=emails,
        fail_silently=False,
    )

    return f'Письма отправлены {len(emails)} подписчикам курса "{course.name}"'
