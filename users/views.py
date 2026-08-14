from rest_framework import generics
from .models import User
from .serializers import UserSerializer


class UserListCreateView(generics.ListCreateAPIView):
    """Получение списка пользователей и создание нового"""
    queryset = User.objects.all()
    serializer_class = UserSerializer


class UserRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """Получение, обновление и удаление пользователя"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
