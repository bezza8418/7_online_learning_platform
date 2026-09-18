from rest_framework import viewsets, generics, permissions
from .models import Course, Lesson
from .serializers import CourseSerializer, LessonSerializer
from users.permissions import IsModerator, IsOwner


class CourseViewSet(viewsets.ModelViewSet):
    """ViewSet для модели Course (полный CRUD)"""
    queryset = Course.objects.all()
    serializer_class = CourseSerializer

    def get_permissions(self):
        """Разные права для разных действий"""
        if self.action == 'create':
            # Создавать курс могут только авторизованные немодераторы
            self.permission_classes = [permissions.IsAuthenticated, ~IsModerator]
        elif self.action == 'destroy':
            # Удалять курс могут только владельцы (немодераторы)
            self.permission_classes = [permissions.IsAuthenticated, ~IsModerator, IsOwner]
        elif self.action in ['update', 'partial_update']:
            # Редактировать могут модераторы ИЛИ владельцы
            self.permission_classes = [permissions.IsAuthenticated, IsModerator | IsOwner]
        else:
            # Просмотр — любым авторизованным
            self.permission_classes = [permissions.IsAuthenticated]
        return super().get_permissions()

    def perform_create(self, serializer):
        """Привязываем создаваемый курс к авторизованному пользователю"""
        serializer.save(owner=self.request.user)


class LessonListCreateView(generics.ListCreateAPIView):
    """Получение списка уроков и создание нового урока"""
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return [permissions.IsAuthenticated(), ~IsModerator()]
        return [permissions.IsAuthenticated()]

    def perform_create(self, serializer):
        """Привязываем создаваемый урок к авторизованному пользователю"""
        serializer.save(owner=self.request.user)


class LessonRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """Получение, обновление и удаление урока"""
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer

    def get_permissions(self):
        if self.request.method == 'DELETE':
            return [permissions.IsAuthenticated(), ~IsModerator(), IsOwner()]
        if self.request.method in ['PUT', 'PATCH']:
            return [permissions.IsAuthenticated(), IsModerator() | IsOwner()]
        return [permissions.IsAuthenticated()]
