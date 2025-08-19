import requests
from django.shortcuts import get_object_or_404

from config.settings import STRIPE_SECRET_KEY
from lms.models import Course, Payment


def create_payment(user, course_id):
    # Получаем курс
    course = get_object_or_404(Course, id=course_id)

    # Создаем продукт в Stripe
    product_data = {
        "name": course.name,  # Название курса
        "description": course.description,  # Описание курса
    }
    product_response = requests.post(
        "https://api.stripe.com/v1/products",
        data=product_data,
        headers={"Authorization": f"Bearer {STRIPE_SECRET_KEY}"},
    )
    if product_response.status_code != 200:
        return {"error": "Failed to create product", "details": product_response.json()}
    product = product_response.json()

    # Создаем цену в Stripe
    price_data = {
        "unit_amount": int(course.price * 100),  # Цена в копейках
        "currency": "rub",  # Валюта
        "product": product["id"],  # ID созданного продукта
    }
    price_response = requests.post(
        "https://api.stripe.com/v1/prices",
        data=price_data,
        headers={"Authorization": f"Bearer {STRIPE_SECRET_KEY}"},
    )
    if price_response.status_code != 200:
        return {"error": "Failed to create price", "details": price_response.json()}
    price = price_response.json()

    # Создаем сессию для оплаты в Stripe
    session_data = {
        "payment_method_types[]": ["card"],
        "line_items[0][price]": price["id"],
        "line_items[0][quantity]": 1,
        "mode": "payment",
        "success_url": "http://127.0.0.1:8000/success",
        "cancel_url": "http://127.0.0.1:8000/cancel",
    }
    session_response = requests.post(
        "https://api.stripe.com/v1/checkout/sessions",
        data=session_data,
        headers={"Authorization": f"Bearer {STRIPE_SECRET_KEY}"},
    )

    if session_response.status_code != 200:
        return {"error": f"Failed to create session: {session_response.json()}"}

    session = session_response.json()

    # Сохраняем платеж в базе данных
    payment = Payment.objects.create(
        user=user,
        paid_course_id=course_id,
        amount=course.price,
        payment_method="transfer",
        session_id=session["id"],
        link=session["url"],
    )

    # Возвращаем ссылку на оплату
    return {
        "payment_link": session["url"],
        "payment_id": payment.id,
    }