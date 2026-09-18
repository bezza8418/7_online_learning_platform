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
            self.permission_classes = [permissions.IsAuthenticated, ~IsModerator]
        elif self.action == 'destroy':
            self.permission_classes = [permissions.IsAuthenticated, ~IsModerator, IsOwner]
        elif self.action in ['update', 'partial_update']:
            self.permission_classes = [permissions.IsAuthenticated, IsModerator | IsOwner]
        else:
            self.permission_classes = [permissions.IsAuthenticated]
        return super().get_permissions()

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class LessonListCreateView(generics.ListCreateAPIView):
    """Получение списка уроков и создание нового урока"""
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [permissions.IsAuthenticated]

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
            self.permission_classes = [permissions.IsAuthenticated]
        return super().get_permissions()
