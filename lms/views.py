from rest_framework import viewsets
from .models import Course
from .serializers import CourseSerializer


class CourseViewSet(viewsets.ModelViewSet):
    """ViewSet для модели Course (полный CRUD)"""
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
