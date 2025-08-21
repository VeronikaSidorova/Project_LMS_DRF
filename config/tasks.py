from datetime import timedelta

from celery import shared_task
from django.core.mail import send_mail
from django.utils import timezone

from config.settings import EMAIL_HOST_USER
from users.models import User


@shared_task
def send_update_letter(course_name, user_emails):
    subject = f"Обновление курса: {course_name}"
    message = f"Курс '{course_name}' был обновлён. Проверьте обновлённые материалы!"
    send_mail(subject, message, EMAIL_HOST_USER, user_emails)


@shared_task
def check_inactive_users():
    now = timezone.now()
    month_ago = now - timedelta(days=30)
    inactive_users = User.objects.filter(last_login__lt=month_ago, is_active=True)
    print(inactive_users)

    for user in inactive_users:
        user.is_active = False
        user.save()
