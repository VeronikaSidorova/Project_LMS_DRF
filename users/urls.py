from django.urls import path

from lms.apps import LmsConfig
from users.views import (PaymentCreateApiView, PaymentListApiView,
                         UserCreateApiView, UserDestroyApiView,
                         UserListApiView, UserRetrieveApiView,
                         UserUpdateApiView)

app_name = LmsConfig.name

urlpatterns = [
    path("", UserListApiView.as_view(), name="users_list"),
    path("<int:pk>/", UserRetrieveApiView.as_view(), name="users_retrieve"),
    path("create/", UserCreateApiView.as_view(), name="users_create"),
    path(
        "<int:pk>/delete/",
        UserDestroyApiView.as_view(),
        name="users_delete",
    ),
    path("<int:pk>/update/", UserUpdateApiView.as_view(), name="users_update"),
    path("payments/create/", PaymentCreateApiView.as_view(), name="payment_create"),
    path("payments/", PaymentListApiView.as_view(), name="payment_list"),
]
