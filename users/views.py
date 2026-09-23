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
