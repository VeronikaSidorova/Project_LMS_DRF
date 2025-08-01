from rest_framework.serializers import ModelSerializer

from users.models import User, Payment


class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "email", "phone", "city", )


class PaymentSerializer(ModelSerializer):
    class Meta:
        model = Payment
        fields = '__all__'


class UserProfileSerializer(ModelSerializer):
    payments = PaymentSerializer(source='payment_set', many=True, read_only=True)

    class Meta:
        model = User
        fields = ("id", "email", "payments", )
