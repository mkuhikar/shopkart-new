from django.shortcuts import render, redirect, get_object_or_404
from .forms import RegistrationForm, UserForm, UserProfileForm, PasswordForm
from .models import Account, UserProfile
from django.contrib.auth.decorators import login_required
from django.contrib import messages, auth
from django.http import HttpResponse, FileResponse

from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage
from carts.models import Cart, CartItem
from carts.views import _cart_id
import requests
from orders.models import Order, OrderProduct
from django.utils.crypto import get_random_string

from django.conf import settings
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.core.files import File
from io import BytesIO
import os
from .tasks import *



# Create your views here.
def delayprogram(request):
    sleepy.delay(10)
    return HttpResponse("<h1>Testing celery</h1>")
def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            phone_number = form.cleaned_data['phone_number']
            username = email.split("@")[0]
            user = Account.objects.create_user(first_name=first_name,last_name=last_name,email=email,username=username,password=password)
            user.phone_number = phone_number
            user.save()
            profile = UserProfile()
            profile.user_id = user.id
            profile.profile_picture = 'userprofile/aa.png'
            profile.save()
            #user ACCOUNT_EMAIL_VERIFICATION
            current_site = get_current_site(request)
            mail_subject = 'Please activate your account'
            message = render_to_string('accounts/account_verification_email.html',{
                'user':user,
                'domain':current_site,
                'uid':urlsafe_base64_encode(force_bytes(user.pk)),
                'token':default_token_generator.make_token(user),
            })
            to_email= email
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.send()

            return redirect('/accounts/login/?command=verification&email='+email)

    else:

        form = RegistrationForm()
    content = {
        'form': form,
        }
    return render(request, 'accounts/register.html', content)
def login(request):
    if request.method =='POST':
        email = request.POST['email']
        password = request.POST['password']
        user = auth.authenticate(email=email,password=password)
        if user is not None:
            try:

                cart = Cart.objects.get(cart_id=_cart_id(request))
                is_cart_item_exists = CartItem.objects.filter(cart=cart).exists()

                if is_cart_item_exists:
                    cart_item_cartid = CartItem.objects.filter(cart=cart)

                    product_variation = []
                    for item in cart_item_cartid:
                        variation = item.variation.all()
                        product_variation.append(list(variation))
                    cart_item_user = CartItem.objects.filter(user=user)
                    ex_var_list = []

                    id = []
                    for item in cart_item_user:
                        existing_variation = item.variation.all()
                        ex_var_list.append(list(existing_variation))
                        id.append(item.id)

                    for pr in product_variation:
                        if pr in ex_var_list:
                            index = ex_var_list.index(pr)
                            item_id = id[index]
                            item = CartItem.objects.get(id=item_id)
                            item.quantity +=1
                            item.user = user
                            item.save()
                        else:
                            cart_item = CartItem.objects.filter(cart=cart)
                            for item in cart_item:
                                item.user = user
                                item.save()


            except:
                pass

            auth.login(request, user)
            messages.success(request, 'You are now logged in' )
            url = request.META.get('HTTP_REFERER')
            try:
                query = requests.utils.urlparse(url).query
                params = dict(x.split('=') for x in query.split('&'))
                if 'next' in params:
                    nextPage = params['next']
                    return redirect(nextPage)
            except:
                return redirect('dashboard')
        else:
            messages.error(request, 'Invalid login credentials')
            return redirect ('login')
    return render(request, 'accounts/login.html')



@login_required(login_url='login')
def logout(request):
    auth.logout(request)
    messages.success(request, 'You are logged out')
    return redirect('login')

def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user=None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, 'Congratulations. Your account has been activated')
        return redirect ('login')
    else:
        message.error(request, 'Invalid activation link')
        return redirect ('register')


    return HttpResponse('ok')

@login_required(login_url='login')
def dashboard(request):
    orders = Order.objects.order_by('-created_at').filter(user_id=request.user.id, is_ordered=True)
    orders_count = orders.count()
    userprofile = UserProfile.objects.get(user=request.user)
    context = {
    'orders_count':orders_count,
    'userprofile':userprofile,
    }
    return render(request,'accounts/dashboard.html', context)

def forgotPassword(request):
    if request.method=='POST':
        email = request.POST['email']
        if Account.objects.filter(email=email).exists():
            user = Account.objects.get(email__exact=email)

            #user ACCOUNT_EMAIL_VERIFICATION
            current_site = get_current_site(request)
            mail_subject = 'Reset Your Password'
            message = render_to_string('accounts/reset_password_email.html',{
                'user':user,
                'domain':current_site,
                'uid':urlsafe_base64_encode(force_bytes(user.pk)),
                'token':default_token_generator.make_token(user),
            })
            to_email= email
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.send()
            messages.success(request, 'Reset password has been sent to your  email address')
            return redirect('login')
        else:
            messages.error(request, 'Account does not exist')
            return redirect('forgotPassword')

    return render(request, 'accounts/forgotPassword.html')

def reset(request, uidb64, token):

    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user=None

    if user is not None and default_token_generator.check_token(user, token):
        request.session['uid'] = uid

        messages.success(request, 'Please reset your password')
        return redirect ('resetPassword')
    else:
        messages.error(request, 'Link has expired. Please try again')
        return redirect ('forgotPassword')

def resetPassword(request):
    if request.method == 'POST':
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password==confirm_password:
            uid = request.session.get('uid')
            user = Account.objects.get(pk=uid)
            user.set_password(password)
            user.save()
            messages.success(request, 'Password reset successful')
            return redirect('dashboard')
        else:
            messages.error("Passwords do not match")
            return redirect('resetPassword')
    else:
        return render(request, 'accounts/resetPassword.html')

def my_orders(request):
    orders = Order.objects.filter(user=request.user.id, is_ordered=True).order_by('-created_at')
    content = {
    'orders':orders
    }
    return render(request, 'accounts/myorders.html',content)

@login_required(login_url='login')
def edit_profile(request):
    userprofile = get_object_or_404(UserProfile, user=request.user)
    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = UserProfileForm(request.POST, request.FILES, instance=userprofile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile has been updated.')
            return redirect('edit_profile')
    else:
        user_form = UserForm(instance=request.user)
        profile_form = UserProfileForm(instance=userprofile)
    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'userprofile': userprofile,
    }
    return render(request, 'accounts/editprofile.html', context)

@login_required(login_url='login')
def change_password(request):
    if request.method == 'POST':
        form = PasswordForm(request.POST)


        if form.is_valid():
            print('valid')
            # had named password as old_password but because it didn't match with model fields ithe fom was not getting valid in views.py
            password = form.cleaned_data['password']

            new_password = form.cleaned_data['new_password']

            user = Account.objects.get(username__exact=request.user.username)
            success = user.check_password(password)

            if success:
                user.set_password(new_password)
                user.save()
                messages.success(request,'Password has been successfully changed')
                return redirect('dashboard')
            else:
                messages.error(request,'Please enter valid password')
                return redirect('change_password')
        else:
            print('not valid')
            print(form.errors)



    else:
        form = PasswordForm()

    content = {'form':form}
    return render(request,'accounts/changepassword.html', content)

@login_required(login_url='login')
def order_detail(request, order_id):
    order_detail = OrderProduct.objects.filter(order__order_number=order_id)
    order = Order.objects.get(order_number=order_id)
    subtotal = 0
    for i in order_detail:
        subtotal += i.product_price * i.quantity

    context = {
        'order_detail': order_detail,
        'order': order,
        'subtotal': subtotal,
    }
    return render(request, 'accounts/order_detail.html', context)

def generate_obj_pdf(request, order_number):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="report.pdf"'
    order_details = OrderProduct.objects.filter(order__order_number=order_number)
    order = Order.objects.get(order_number=order_number)
    template_path = 'accounts/pdf1.html'
    context = {'order_details': order_details}
    pdf = render_to_pdf(template_path, context, response)
    orderstring = str(order.order_number)
    filename = 'Order{}.pdf'
    orderfile = filename.format(orderstring)
    order.receipt.save(orderfile, File(BytesIO(pdf.content)))
    return response

def render_to_pdf(template_path, context, response):
    # Create a Django response object, and specify content_type as pdf

    # find the template and render it.
    template = get_template(template_path)
    html = template.render(context)

    # create a pdf
    pisa_status = pisa.CreatePDF(
       html, dest=response)
    # if error then show some funy view
    if pisa_status.err:
       return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response

@login_required
def order_receipt(request, order_number):
    order = Order.objects.get(order_number=order_number)
    user = order.user
    # if request.user == user:
    #     with open('accounts/a.pdf', 'r') as pdf:
    #         response = HttpResponse(pdf.read(), mimetype='application/pdf')
    #         response['Content-Disposition'] = 'inline;filename=some_file.pdf'
    #         return response
    #     pdf.closed

    if request.user == user:

        f_name = '%s%s' % (settings.AWS_S3_CUSTOM_DOMAIN, "/media/pdfs/Order%s.pdf" % order.order_number)
        return FileResponse(open(f_name, 'rb'), content_type="application/pdf")
    else:
        return HttpResponse('Unauthorized Access', status=401)

def send_receipt(request, order_number):

    send_email_with_attach.delay(order_number)
    # f_name = '%s%s' % (settings.AWS_S3_CUSTOM_DOMAIN, "/media/pdfs/Order%s.pdf" % order.order_number)
# pdf = order.receipt.name
    # msg.content_subtype = "html"
    # # attachment = open(f_name, 'rb')
    # return FileResponse(open(f_name, 'rb'), content_type="application/pdf")
    # msg.attach('%s.pdf' % get_random_string(), attachment.read(),content_type='application/pdf')
    # pdffile="/media/a.pdf"
    # msg.attach_file('media/a.pdf')

    return HttpResponse('email done')
