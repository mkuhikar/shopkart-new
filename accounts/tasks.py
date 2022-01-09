from celery import shared_task
from time import sleep
from django.core.mail import EmailMessage
from orders.models import Order
import requests

@shared_task
def sleepy(duration):
    sleep(duration)
    return None

@shared_task
def send_email_with_attach(order_number):
    order = Order.objects.get(order_number=order_number)
    to_email = order.user.email
    response = requests.get(order.receipt.url)
    msg = EmailMessage('Order receipt', 'Zhal na bhau', to=[to_email])
    msg.attach('My file',response.content,mimetype="application/pdf")
    msg.send()
    return None
