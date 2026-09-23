from rest_framework import viewsets, generics, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Course, Lesson, Subscription
from .serializers import CourseSerializer, LessonSerializer
from users.permissions import IsModerator, IsOwner
from .paginators import StandardResultsSetPagination
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiExample
from rest_framework import serializers


class SubscriptionRequestSerializer(serializers.Serializer):
    """Сериализатор для запроса подписки"""
    course_id = serializers.IntegerField(help_text='ID курса')


class SubscriptionResponseSerializer(serializers.Serializer):
    """Сериализатор для ответа подписки"""
    message = serializers.CharField(help_text='Сообщение о результате')


class CourseViewSet(viewsets.ModelViewSet):
    """ViewSet для модели Course (полный CRUD)"""
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        """Фильтрация: модератор видит всё, обычный — только своё"""
        user = self.request.user
        if user.groups.filter(name='Модераторы').exists():
            return Course.objects.all()
        return Course.objects.filter(owner=user)

    def get_permissions(self):
        if self.action == 'create':
            self.permission_classes = [permissions.IsAuthenticated, ~IsModerator]
        elif self.action == 'destroy':
            self.permission_classes = [permissions.IsAuthenticated, ~IsModerator, IsOwner]
        elif self.action in ['update', 'partial_update']:
            self.permission_classes = [permissions.IsAuthenticated, IsModerator | IsOwner]
        else:
            self.permission_classes = [permissions.IsAuthenticated, IsModerator | IsOwner]
        return super().get_permissions()

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class LessonListCreateView(generics.ListCreateAPIView):
    """Получение списка уроков и создание нового урока"""
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        """Фильтрация: модератор видит всё, обычный — только своё"""
        user = self.request.user
        if user.groups.filter(name='Модераторы').exists():
            return Lesson.objects.all()
        return Lesson.objects.filter(owner=user)

    def get_permissions(self):
        if self.request.method == 'POST':
            self.permission_classes = [permissions.IsAuthenticated, ~IsModerator]
        else:
            self.permission_classes = [permissions.IsAuthenticated]
        return super().get_permissions()

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class LessonRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """Получение, обновление и удаление урока"""
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        if self.request.method == 'DELETE':
            self.permission_classes = [permissions.IsAuthenticated, ~IsModerator, IsOwner]
        elif self.request.method in ['PUT', 'PATCH']:
            self.permission_classes = [permissions.IsAuthenticated, IsModerator | IsOwner]
        else:
            # retrieve — модератор ИЛИ владелец
            self.permission_classes = [permissions.IsAuthenticated, IsModerator | IsOwner]
        return super().get_permissions()


class SubscriptionAPIView(APIView):
    """Управление подпиской на обновления курса"""
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        summary='Управление подпиской на курс',
        description='Если подписка есть — удаляет, если нет — создаёт.',
        request=SubscriptionRequestSerializer,
        responses={
            200: SubscriptionResponseSerializer,
            404: OpenApiResponse(description='Курс не найден'),
        },
        examples=[
            OpenApiExample(
                'Пример запроса',
                value={'course_id': 1},
                request_only=True,
            ),
            OpenApiExample(
                'Пример ответа',
                value={'message': 'подписка добавлена'},
                response_only=True,
            ),
        ],
    )
    def post(self, *args, **kwargs):
        user = self.request.user
        course_id = self.request.data.get('course_id')
        course_item = get_object_or_404(Course, id=course_id)

        subs_item = Subscription.objects.filter(user=user, course=course_item)

        if subs_item.exists():
            subs_item.delete()
            message = 'подписка удалена'
        else:
            Subscription.objects.create(user=user, course=course_item)
            message = 'подписка добавлена'

        return Response({"message": message})
