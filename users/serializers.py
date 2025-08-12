from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from lms.serializers import PaymentSerializer
from users.models import User


class UserSerializer(ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = (
            "password",
            "username",
            "id",
            "email",
            "phone",
            "city",
        )


class UserProfileSerializer(ModelSerializer):
    payments = PaymentSerializer(source="payment_set", many=True, read_only=True)

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "payments",
        )
