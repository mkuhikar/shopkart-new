from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from carts.models import CartItem
from .forms import OrderForm
import datetime
from .models import Order, Payment, OrderProduct
import json
from products.models import Product
from django.core.mail import EmailMessage
from django.template.loader import render_to_string



# Create your views here.

def place_order(request, total = 0, quantity = 0):
    current_user = request.user
    cart_items = CartItem.objects.filter(user=current_user)
    cart_count = cart_items.count()
    if cart_count<=0:
        return redirect('store')
    grand_total = 0
    tax = 0

    for cart_item in cart_items:
        total += (cart_item.product.price*cart_item.quantity)
        quantity += cart_item.quantity
    tax = (12*total)/100
    grand_total = total + tax

    if request.method == 'POST':

        form = OrderForm(request.POST)

        if form.is_valid():
            data = Order()
            data.user = current_user
            data.first_name = form.cleaned_data['first_name']
            data.last_name = form.cleaned_data['last_name']
            data.phone = form.cleaned_data['phone']
            data.email = form.cleaned_data['email']
            data.address_line_1 = form.cleaned_data['address_line_1']
            data.address_line_2 = form.cleaned_data['address_line_2']
            data.country = form.cleaned_data['country']
            data.state = form.cleaned_data['state']
            data.city = form.cleaned_data['city']

            data.order_total = grand_total
            data.tax = tax
            data.ip = request.META.get('REMOTE_ADDR')
            data.save()

            yr = int(datetime.date.today().strftime('%Y'))
            dt = int(datetime.date.today().strftime('%d'))
            mt = int(datetime.date.today().strftime('%m'))

            d = datetime.date(yr,mt,dt)

            current_date = d.strftime("%Y%m%d")

            order_number = current_date + str(data.id)
            data.order_number = order_number

            data.save()
            order = Order.objects.get(order_number=order_number, user=current_user,is_ordered=False)
            content = {
            'order':order,
            'cart_items':cart_items,
            'total':total,
            'tax':tax,
            'grand_total':grand_total,

            }
            return render(request, 'store/review_order.html', content)

    else:
        return redirect('checkout')

def payment(request):
    body = json.loads(request.body)
    order = Order.objects.get(user=request.user,order_number=body['orderID'],is_ordered=False)
    payment = Payment(
        payment_id = body['transID'],
        user = request.user,
        payment_method = body['payment_method'],
        amount_paid = order.order_total,
        status = body['status'],
    )
    print(payment)
    payment.save()
    order.payment = payment
    order.is_ordered = True
    # order has to be saved or it wont get reflected in backend
    order.save()

    cart_items = CartItem.objects.filter(user=request.user)
    for item in cart_items:
        orderproduct = OrderProduct()
        # the below method can be used with payment also above
        orderproduct.user = request.user
        orderproduct.order = order
        orderproduct.product = item.product
        orderproduct.payment = payment
        orderproduct.product_price = item.product.price
        orderproduct.quantity = item.quantity
        orderproduct.ordered = True
        orderproduct.save()

        # Save variations
        product_variations = item.variation.all()
        orderproduct = OrderProduct.objects.get(id=orderproduct.id)
        orderproduct.variation.set(product_variations)
        orderproduct.save()

        # Reduce stock
        product = Product.objects.get(id=item.product.id)
        product.stock -=item.quantity
        product.save()

        # Delete cart items
    CartItem.objects.filter(user=request.user).delete()

    mail_subject = 'Your Order Details'
    user = request.user
    message = render_to_string('orders/order_received_email.html',{
        'user':user,
        'order':order

    })
    to_email= user.email
    send_email = EmailMessage(mail_subject, message, to=[to_email])
    send_email.send()

# Send order number and payment id to the order_complete
    data = {
    'order_number':order.order_number,
    'transID':payment.payment_id,
    }

    return JsonResponse(data)


def order_complete(request):
    order_number = request.GET.get('order_number')
    transID = request.GET.get('payment_id')
    try:
        order = Order.objects.get(order_number = order_number, is_ordered=True)
        # The order's id is used to filter order products whose foreign key order_id column has same value
        ordered_products = OrderProduct.objects.filter(order_id=order.id)
        payment = Payment.objects.get(payment_id=transID)
        subtotal = 0
        for i in ordered_products:
            subtotal += i.product_price * i.quantity



        context = {
        'order':order,
        'ordered_products':ordered_products,
        'order_number':order.order_number,
        'transID':payment.payment_id,
        'payment':payment,
        'subtotal':subtotal,
        }
        return render(request,'orders/order_complete.html', context)
    except(Payment.DoesNotExist, Order.DoesNotExist):
        return redirect('home')
