from django.db import models

from users.models import User


class Course(models.Model):
    name = models.CharField(
        max_length=100,
        verbose_name="Название курса",
        help_text="Укажите название курса",
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name="Описание курса",
        help_text="Укажите описание курса",
    )
    preview_image = models.ImageField(
        upload_to="lms/image",
        blank=True,
        null=True,
        verbose_name="Превью",
        help_text="Загрузите превью курса",
    )
    owner = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Владелец курса",
        help_text="Укажите владельца курса",
    )

    class Meta:
        verbose_name = "Курс"
        verbose_name_plural = "Курсы"


class Lesson(models.Model):
    name = models.CharField(
        max_length=100,
        verbose_name="Название урока",
        help_text="Укажите название урока",
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name="Описание урока",
        help_text="Укажите описание урока",
    )
    preview_image = models.ImageField(
        upload_to="lms/image",
        blank=True,
        null=True,
        verbose_name="Превью",
        help_text="Загрузите превью урока",
    )
    video_url = models.URLField(blank=True, null=True)
    course = models.ForeignKey(
        Course,
        verbose_name="Название курса",
        related_name="lessons",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    owner = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Владелец урока",
        help_text="Укажите владельца урока",
    )

    class Meta:
        verbose_name = "Урок"
        verbose_name_plural = "Уроки"


class Payment(models.Model):
    PAYMENT_METHODS = [
        ("cash", "Наличные"),
        ("transfer", "Перевод на счет"),
    ]

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name="Пользователь"
    )
    payment_date = models.DateTimeField(auto_now_add=True, verbose_name="Дата оплаты")
    paid_course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        verbose_name="Оплаченный курс",
        null=True,
        blank=True,
    )
    paid_lesson = models.ForeignKey(
        Lesson,
        on_delete=models.CASCADE,
        verbose_name="Оплаченный урок",
        null=True,
        blank=True,
    )
    amount = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name="Сумма оплаты"
    )
    payment_method = models.CharField(
        max_length=10, choices=PAYMENT_METHODS, verbose_name="Способ оплаты"
    )

    class Meta:
        verbose_name = "Платеж"
        verbose_name_plural = "Платежи"
