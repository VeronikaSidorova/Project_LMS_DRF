from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status
from rest_framework.generics import (
    CreateAPIView,
    DestroyAPIView,
    ListAPIView,
    RetrieveAPIView,
    UpdateAPIView,
    get_object_or_404,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from config.tasks import send_update_letter
from lms.models import Course, Lesson, Payment, Subscription
from lms.paginations import CustomPagination
from lms.serializers import CourseSerializer, LessonSerializer, PaymentSerializer
from lms.services import create_payment
from users.permissions import IsModer, IsOwner


class CourseViewSet(ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    pagination_class = CustomPagination

    def perform_create(self, serializer):
        course = serializer.save()
        course.owner = self.request.user
        course.save()

    def perform_update(self, serializer):
        course = serializer.save()
        # Получаем всех пользователей, подписанных на обновления курса
        subscribed_users = Subscription.objects.filter(course=course).values_list(
            "user__email", flat=True
        )

        # Отправляем асинхронное письмо
        send_update_letter().delay(course.title, list(subscribed_users))

    def get_queryset(self):
        if self.request.user.groups.filter(name="moders").exists():
            return Course.objects.all()
        return Course.objects.filter(owner=self.request.user)

    def get_permissions(self):
        if self.action == "create":
            self.permission_classes = (~IsModer,)
        elif self.action in ["update", "retrieve"]:
            self.permission_classes = (IsModer | IsOwner,)
        elif self.action == "destroy":
            self.permission_classes = (~IsModer | IsOwner,)
        return super().get_permissions()


class LessonCreateApiView(CreateAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = (~IsModer, IsAuthenticated)

    def perform_create(self, serializer):
        lesson = serializer.save(
            owner=self.request.user
        )  # Сохраняем урок и устанавливаем владельца

        # Получаем курс, к которому добавляется урок
        course = get_object_or_404(Course, id=self.request.data.get("course"))

        # Получаем всех пользователей, подписанных на обновления курса
        subscribed_users = Subscription.objects.filter(course=course).values_list(
            "user__email", flat=True
        )

        # Отправляем асинхронное письмо
        send_update_letter.delay(course.name, list(subscribed_users))

        return lesson


class LessonListApiView(ListAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    pagination_class = CustomPagination

    def get_queryset(self):
        if self.request.user.groups.filter(name="moders").exists():
            return Lesson.objects.all()
        return Lesson.objects.filter(owner=self.request.user)


class LessonRetrieveApiView(RetrieveAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = (IsAuthenticated, IsModer | IsOwner)


class LessonUpdateApiView(UpdateAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = (IsAuthenticated, IsModer | IsOwner)


class LessonDestroyApiView(DestroyAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = (IsAuthenticated, IsOwner | ~IsModer)


class PaymentCreateApiView(CreateAPIView):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = (~IsModer, IsAuthenticated)

    def perform_create(self, serializer):
        payment = serializer.save()
        payment.owner = self.request.user
        payment.save()


class CreatePaymentApiView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, course_id):
        # Получаем курс по ID
        course = get_object_or_404(Course, id=course_id)

        try:
            # Вызываем сервисную функцию для создания платежа
            payment_info = create_payment(user=request.user, course_id=course.id)
            if "error" in payment_info:
                return Response(
                    {"error": payment_info["error"]}, status=status.HTTP_400_BAD_REQUEST
                )

            # Возвращаем ответ с ссылкой на оплату
            return Response(payment_info, status=status.HTTP_201_CREATED)
        except Exception as e:
            # Обработка ошибок и возврат ответа с ошибкой
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class PaymentListApiView(ListAPIView):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = (
        "paid_course",
        "paid_lesson",
        "payment_method",
    )  # фильтрация по курсу, уроку, способу оплаты
    ordering_fields = ("payment_date",)  # сортировка по дате оплаты
    ordering = ("-payment_date",)


class SubscriptionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user
        course_id = request.data.get("id")
        course_item = get_object_or_404(Course, id=course_id)

        # Проверяем, существует ли подписка для текущего пользователя на курс
        subs_item = Subscription.objects.filter(user=user, course=course_item)

        # Если подписка существует, удаляем ее
        if subs_item.exists():
            subs_item.delete()
            message = "Подписка удалена"
        # Если подписки нет, создаем новую
        else:
            Subscription.objects.create(user=user, course=course_item)
            message = "Подписка добавлена"

        return Response({"message": message}, status=status.HTTP_200_OK)
