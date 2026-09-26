from django.urls import path
from .views import (
    UserRegistrationView,
    UserListCreateView,
    UserRetrieveUpdateDestroyView,
    PaymentListCreateView,
    PaymentCreateAPIView,
    PaymentStatusAPIView,
)

urlpatterns = [
    # Регистрация (без авторизации)
    path('register/', UserRegistrationView.as_view(), name='user-register'),
    # CRUD пользователей
    path('users/', UserListCreateView.as_view(), name='user-list-create'),
    path('users/<int:pk>/', UserRetrieveUpdateDestroyView.as_view(), name='user-retrieve-update-destroy'),
    # Платежи
    path('payments/', PaymentListCreateView.as_view(), name='payment-list-create'),
    path('payments/create/', PaymentCreateAPIView.as_view(), name='payment-create'),
    path('payments/status/', PaymentStatusAPIView.as_view(), name='payment-status'),
]
