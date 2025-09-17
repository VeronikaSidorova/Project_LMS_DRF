from django.urls import path
from rest_framework.routers import SimpleRouter

from lms.apps import LmsConfig
from lms.views import (
    CourseViewSet,
    CreatePaymentApiView,
    LessonCreateApiView,
    LessonDestroyApiView,
    LessonListApiView,
    LessonRetrieveApiView,
    LessonUpdateApiView,
    PaymentCreateApiView,
    PaymentListApiView,
    SubscriptionView,
)

app_name = LmsConfig.name

router = SimpleRouter()
router.register("", CourseViewSet)

urlpatterns = [
    path("lessons/", LessonListApiView.as_view(), name="lessons_list"),
    path("lessons/<int:pk>/", LessonRetrieveApiView.as_view(), name="lessons_retrieve"),
    path("lessons/create/", LessonCreateApiView.as_view(), name="lessons_create"),
    path(
        "lessons/<int:pk>/delete/",
        LessonDestroyApiView.as_view(),
        name="lessons_delete",
    ),
    path(
        "lessons/<int:pk>/update/", LessonUpdateApiView.as_view(), name="lessons_update"
    ),
    path("payments/create/", PaymentCreateApiView.as_view(), name="payment_create"),
    path(
        "payments/create/<int:course_id>/",
        CreatePaymentApiView.as_view(),
        name="create_course_payment",
    ),
    path("payments/", PaymentListApiView.as_view(), name="payment_list"),
    path("subscription/", SubscriptionView.as_view(), name="subscription"),
]

urlpatterns += router.urls
