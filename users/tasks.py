from datetime import timedelta

from celery import shared_task
from django.utils import timezone

from users.models import User


@shared_task
def check_inactive_users():
    """Функция, которая проверяет последний вход пользователя и блокирует его, если не заходил более 30 дней."""
    now = timezone.now()
    month_ago = now - timedelta(days=30)
    inactive_users = User.objects.filter(last_login__lt=month_ago, is_active=True)

    for user in inactive_users:
        user.is_active = False
        user.save()
