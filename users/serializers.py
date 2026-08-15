from rest_framework import serializers
from .models import User, Payment


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'phone', 'city', 'avatar']


class PaymentSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Payment"""

    class Meta:
        model = Payment
        fields = '__all__'
