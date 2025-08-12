from rest_framework.serializers import ModelSerializer, SerializerMethodField

from lms.models import Course, Lesson, Payment


class LessonSerializer(ModelSerializer):
    class Meta:
        model = Lesson
        fields = "__all__"


class CourseSerializer(ModelSerializer):
    lesson_count = SerializerMethodField()
    lessons = LessonSerializer(many=True, read_only=True)

    class Meta:
        model = Course
        fields = "__all__"

    def get_lesson_count(self, obj):
        return obj.lessons.count()


class PaymentSerializer(ModelSerializer):
    class Meta:
        model = Payment
        fields = "__all__"
