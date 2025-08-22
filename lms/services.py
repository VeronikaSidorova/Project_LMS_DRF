import requests
from django.shortcuts import get_object_or_404

from config.settings import STRIPE_SECRET_KEY
from lms.models import Course, Payment


def create_product(course):
    """Функция создания продукта"""
    product_data = {
        "name": course.name,
        "description": course.description,
    }
    product_response = requests.post(
        "https://api.stripe.com/v1/products",
        data=product_data,
        headers={"Authorization": f"Bearer {STRIPE_SECRET_KEY}"},
    )
    if product_response.status_code != 200:
        return None, {
            "error": "Failed to create product",
            "details": product_response.json(),
        }

    return product_response.json(), None


def create_price(product_id, course_price):
    """Функция создания цены"""
    price_data = {
        "unit_amount": int(course_price * 100),
        "currency": "rub",
        "product": product_id,
    }
    price_response = requests.post(
        "https://api.stripe.com/v1/prices",
        data=price_data,
        headers={"Authorization": f"Bearer {STRIPE_SECRET_KEY}"},
    )
    if price_response.status_code != 200:
        return None, {
            "error": "Failed to create price",
            "details": price_response.json(),
        }

    return price_response.json(), None


def create_checkout_session(price_id):
    """Функция создания сессии"""
    session_data = {
        "payment_method_types[]": ["card"],
        "line_items[0][price]": price_id,
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
        return None, {"error": f"Failed to create session: {session_response.json()}"}

    return session_response.json(), None


def create_payment(user, course_id):
    """Функция создания платежа"""
    # Получаем курс
    course = get_object_or_404(Course, id=course_id)

    # Создаем продукт
    product, error = create_product(course)
    if error:
        return error

    # Создаем цену
    price, error = create_price(product["id"], course.price)
    if error:
        return error

    # Создаем сессию для оплаты
    session, error = create_checkout_session(price["id"])
    if error:
        return error

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
