from celery import shared_task
from django.core.mail import send_mail

from config.settings import EMAIL_HOST_USER


@shared_task
def send_update_letter(course_name, user_emails):
    """Функция для отправки письма об обновлениях курса."""
    subject = f"Обновление курса: {course_name}"
    message = f"Курс '{course_name}' был обновлён. Проверьте обновлённые материалы!"
    send_mail(subject, message, EMAIL_HOST_USER, user_emails)
