from rest_framework import generics, permissions
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from .models import User, Payment
from .serializers import (
    UserSerializer,
    UserPublicSerializer,
    UserRegistrationSerializer,
    PaymentSerializer,
)
from .filters import PaymentFilter
from .permissions import IsOwnerProfile
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiParameter

class UserRegistrationView(generics.CreateAPIView):
    """Регистрация нового пользователя (доступна без авторизации)"""
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]

    @extend_schema(
        summary='Регистрация пользователя',
        description='Создаёт нового пользователя. Доступно без авторизации.',
        responses={
            201: UserRegistrationSerializer,
            400: OpenApiResponse(description='Ошибка валидации'),
        },
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class UserListCreateView(generics.ListCreateAPIView):
    """Список пользователей и создание нового"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]


class UserRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """Получение, обновление и удаление пользователя"""
    queryset = User.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        """Для просмотра чужого профиля — публичный сериализатор"""
        if self.request.method == 'GET' and self.get_object() != self.request.user:
            return UserPublicSerializer
        return UserSerializer

    def get_permissions(self):
        """Редактировать можно только свой профиль"""
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [permissions.IsAuthenticated(), IsOwnerProfile()]
        return [permissions.IsAuthenticated()]


class PaymentListCreateView(generics.ListCreateAPIView):
    """Список платежей с фильтрацией и создание нового платежа"""
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = PaymentFilter
    ordering_fields = ['payment_date']

    @extend_schema(
        summary='Список платежей',
        description='Возвращает список платежей с фильтрацией и сортировкой.',
        parameters=[
            OpenApiParameter(name='paid_course', description='ID курса', required=False, type=int),
            OpenApiParameter(name='paid_lesson', description='ID урока', required=False, type=int),
            OpenApiParameter(name='payment_method', description='Способ оплаты (cash/transfer)', required=False, type=str),
            OpenApiParameter(name='ordering', description='Сортировка по дате (payment_date/-payment_date)', required=False, type=str),
        ],
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiExample
from .services import (
    create_stripe_product,
    create_stripe_price,
    create_stripe_session,
)
from lms.models import Course, Lesson
import stripe


class PaymentCreateAPIView(APIView):
    """
    Создание платежа через Stripe.

    Принимает ID курса или урока, создаёт продукт, цену и сессию в Stripe,
    сохраняет ссылку на оплату в модели Payment и возвращает её пользователю.
    """
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        summary='Создание платежа через Stripe',
        description='Создаёт продукт, цену и сессию в Stripe, возвращает ссылку на оплату.',
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'course_id': {'type': 'integer', 'description': 'ID курса'},
                    'lesson_id': {'type': 'integer', 'description': 'ID урока'},
                    'amount': {'type': 'integer', 'description': 'Сумма в рублях'},
                },
                'required': ['amount'],
            }
        },
        responses={
            200: OpenApiResponse(description='Ссылка на оплату и данные платежа'),
            400: OpenApiResponse(description='Ошибка валидации'),
            404: OpenApiResponse(description='Курс или урок не найден'),
        },
        examples=[
            OpenApiExample(
                'Пример запроса',
                value={'course_id': 1, 'amount': 5000},
                request_only=True,
            ),
            OpenApiExample(
                'Пример ответа',
                value={
                    'payment_id': 1,
                    'payment_link': 'https://checkout.stripe.com/...',
                    'amount': 5000,
                },
                response_only=True,
            ),
        ],
    )
    def post(self, request, *args, **kwargs):
        user = request.user
        course_id = request.data.get('course_id')
        lesson_id = request.data.get('lesson_id')
        amount = request.data.get('amount')

        # Валидация
        if not amount:
            return Response(
                {'error': 'Поле amount обязательно'},
                status=400
            )

        course = None
        lesson = None

        if course_id:
            course = get_object_or_404(Course, id=course_id)
        elif lesson_id:
            lesson = get_object_or_404(Lesson, id=lesson_id)
        else:
            return Response(
                {'error': 'Укажите course_id или lesson_id'},
                status=400
            )

        # Определяем название продукта
        product_name = course.name if course else lesson.name

        try:
            # 1. Создаём продукт в Stripe
            product = create_stripe_product(product_name)

            # 2. Создаём цену в Stripe (в копейках!)
            price = create_stripe_price(product.id, amount * 100)

            # 3. Создаём сессию оплаты
            success_url = 'http://127.0.0.1:8000/api/payments/success/'
            cancel_url = 'http://127.0.0.1:8000/api/payments/cancel/'
            session = create_stripe_session(price.id, success_url, cancel_url)

            # 4. Сохраняем платёж в нашей БД
            payment = Payment.objects.create(
                user=user,
                paid_course=course,
                paid_lesson=lesson,
                amount=amount,
                payment_method='transfer',
                stripe_product_id=product.id,
                stripe_price_id=price.id,
                stripe_session_id=session.id,
                payment_link=session.url,
            )

            return Response({
                'payment_id': payment.id,
                'payment_link': session.url,
                'amount': amount,
            })

        except stripe.StripeError as e:
            return Response(
                {'error': f'Ошибка Stripe: {str(e)}'},
                status=400
            )


from .services import retrieve_stripe_session


class PaymentStatusAPIView(APIView):
    """
    Проверка статуса платежа через Stripe.

    Принимает ID сессии Stripe, возвращает статус платежа.
    """
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        summary='Проверка статуса платежа',
        description='Получает данные о сессии из Stripe по её ID.',
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'session_id': {'type': 'string', 'description': 'ID сессии в Stripe'},
                },
                'required': ['session_id'],
            }
        },
        responses={
            200: OpenApiResponse(description='Данные о статусе платежа'),
            400: OpenApiResponse(description='Ошибка'),
            404: OpenApiResponse(description='Сессия не найдена'),
        },
        examples=[
            OpenApiExample(
                'Пример запроса',
                value={'session_id': 'cs_test_...'},
                request_only=True,
            ),
            OpenApiExample(
                'Пример ответа',
                value={
                    'session_id': 'cs_test_...',
                    'payment_status': 'paid',
                    'amount_total': 500000,
                    'currency': 'rub',
                },
                response_only=True,
            ),
        ],
    )
    def post(self, request, *args, **kwargs):
        session_id = request.data.get('session_id')

        if not session_id:
            return Response(
                {'error': 'Поле session_id обязательно'},
                status=400
            )

        try:
            session = retrieve_stripe_session(session_id)
            return Response({
                'session_id': session.id,
                'payment_status': session.payment_status,
                'amount_total': session.amount_total,
                'currency': session.currency,
            })
        except stripe.StripeError as e:
            return Response(
                {'error': f'Ошибка Stripe: {str(e)}'},
                status=400
            )
