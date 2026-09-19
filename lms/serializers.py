from rest_framework import serializers
from .models import Course, Lesson, Subscription
from .validators import YouTubeValidator


class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = '__all__'
        validators = [
            YouTubeValidator(field='video_link')
        ]


class SubscriptionSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Subscription"""

    class Meta:
        model = Subscription
        fields = '__all__'


class CourseSerializer(serializers.ModelSerializer):
    lessons = LessonSerializer(source='lessons.all', many=True, read_only=True)
    lessons_count = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = '__all__'

    def get_lessons_count(self, obj):
        return obj.lessons.count()
