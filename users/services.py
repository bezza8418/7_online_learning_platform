import stripe
from django.conf import settings

stripe.api_key = settings.STRIPE_SECRET_KEY


def create_stripe_product(name: str) -> stripe.Product:
    """
    Создаёт продукт в Stripe.

    :param name: Название продукта (например, название курса)
    :return: Объект Product из Stripe
    """
    product = stripe.Product.create(name=name)
    return product


def create_stripe_price(product_id: str, amount: int) -> stripe.Price:
    """
    Создаёт цену в Stripe.

    :param product_id: ID продукта в Stripe
    :param amount: Сумма в копейках (рубли * 100)
    :return: Объект Price из Stripe
    """
    price = stripe.Price.create(
        product=product_id,
        unit_amount=amount,
        currency='rub',
    )
    return price


def create_stripe_session(price_id: str, success_url: str, cancel_url: str) -> stripe.checkout.Session:
    """
    Создаёт сессию оплаты в Stripe.

    :param price_id: ID цены в Stripe
    :param success_url: URL для перенаправления после успешной оплаты
    :param cancel_url: URL для перенаправления при отмене
    :return: Объект Session из Stripe
    """
    session = stripe.checkout.Session.create(
        line_items=[{'price': price_id, 'quantity': 1}],
        mode='payment',
        success_url=success_url,
        cancel_url=cancel_url,
    )
    return session


def retrieve_stripe_session(session_id: str) -> stripe.checkout.Session:
    """
    Получает данные о сессии оплаты из Stripe.

    :param session_id: ID сессии в Stripe
    :return: Объект Session из Stripe
    """
    session = stripe.checkout.Session.retrieve(session_id)
    return session
