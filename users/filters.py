from django_filters import rest_framework as filters
from .models import Payment


class PaymentFilter(filters.FilterSet):
    """Фильтр для модели Payment"""

    # Сортировка по дате (поле для ordering)
    ordering = filters.OrderingFilter(
        fields=('payment_date',),
        field_labels={'payment_date': 'Дата оплаты'}
    )

    # Фильтр по курсу
    paid_course = filters.NumberFilter(field_name='paid_course__id')

    # Фильтр по уроку
    paid_lesson = filters.NumberFilter(field_name='paid_lesson__id')

    # Фильтр по способу оплаты
    payment_method = filters.ChoiceFilter(choices=Payment.PAYMENT_METHODS)

    class Meta:
        model = Payment
        fields = ['paid_course', 'paid_lesson', 'payment_method']
