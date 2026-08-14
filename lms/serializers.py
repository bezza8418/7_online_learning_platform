from rest_framework import serializers
from .models import Course, Lesson


class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = '__all__'


class CourseSerializer(serializers.ModelSerializer):
    # Вложенный сериализатор для уроков
    lessons = LessonSerializer(source='lessons.all', many=True, read_only=True)

    class Meta:
        model = Course
        fields = '__all__'
