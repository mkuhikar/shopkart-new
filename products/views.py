from django.shortcuts import render, get_object_or_404, redirect
from .models import Product, ReviewRating, ProductGallery
from category.models import Category
from django.urls import reverse
from carts.models import CartItem
from carts.views import _cart_id
from django.http import HttpResponse
from django.db.models import Q
from django.core.paginator import EmptyPage,Paginator, PageNotAnInteger
from .forms import ReviewForm
from django.contrib import messages
from orders.models import OrderProduct


def store(request, category_slug=None):
    categories = None
    products = None
    if category_slug!= None:
        categories = get_object_or_404(Category,slug=category_slug)
        products = Product.objects.filter(category=categories, is_available=True)
        paginator = Paginator(products,3)
        page = request.GET.get('page')
        paged_products = paginator.get_page(page)
        product_count = products.count()
    else:
        products = Product.objects.all().filter(is_available=True)
        paginator = Paginator(products,3)
        page = request.GET.get('page')
        paged_products = paginator.get_page(page)
        product_count = products.count()
    content = {'products':paged_products,
    'product_count':product_count
    }

    return render(request, 'store/store.html', content)
def product_detail(request, category_slug,product_slug):
    # To get to product category's slug double underscore is used
    try:
        single_product = Product.objects.get(category__slug=category_slug,slug=product_slug)
        product_bought = OrderProduct.objects.filter(user__id=request.user.id,product__id=single_product.id).exists()
        # because we are accessing cart's cart_id we have to use cart__cart_id and to check if it exists then filter has to be used instaed of get
        in_cart = CartItem.objects.filter(cart__cart_id=_cart_id(request), product=single_product).exists()
        is_reviews = ReviewRating.objects.filter(product=single_product).exists()
        product_gallery = ProductGallery.objects.filter(product_id=single_product.id)

        if is_reviews:
            reviews = ReviewRating.objects.filter(product=single_product, status=True)
        else:
            reviews = False

    except Exception  as e:
        raise e
    content = {
    'single_product':single_product,
    'in_cart':in_cart,
    'product_bought':product_bought,
    'reviews':reviews,
    'product_gallery':product_gallery,
    }
    return render(request, 'store/product_detail.html',content)
# Create your views here.

def search(request):
    if 'keyword' in request.GET:
        keyword = request.GET['keyword']
        if keyword:
            products = Product.objects.order_by('-created_date').filter(Q(description__icontains=keyword)|Q(product_name__icontains=keyword))
            product_count = products.count()
    content = {
    'products': products,
    'product_count':product_count
    }
    return render(request,'store/store.html',content)

def submit_review(request, product_id):
    url = request.META.get('HTTP_REFERER')
    if request.method == 'POST':
        try:
            review = ReviewRating.objects.get(user__id=request.user.id,product__id=product_id)
            form = ReviewForm(request.POST, instance=review)
            form.save()
            messages.success(request, 'Thank you! Your review is valuable to us')
            return redirect(url)
        except ReviewRating.DoesNotExist:
            form = ReviewForm(request.POST)
            product_bought = OrderProduct.objects.filter(user__id=request.user.id,product__id=product_id).exists()
            print(product_bought)
            if product_bought:
                if form.is_valid():
                    data = ReviewRating()
                    data.subject = form.cleaned_data['subject']
                    data.rating = form.cleaned_data['rating']
                    data.review = form.cleaned_data['review']
                    data.ip = request.META.get('REMOTE_ADDR')
                    data.product_id = product_id
                    data.user_id = request.user.id
                    data.save()
                    messages.success(request, 'Your review has been successfully added')
                    return redirect(url)
            else:
                messages.error(request, 'Only verified purchasers can post reviews')
                return redirect(url)
