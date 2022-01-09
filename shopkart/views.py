from django.shortcuts import render
from products.models import Product, ReviewRating

def home(request):
	products = Product.objects.all().filter(is_available=True).order_by('-created_date')
	reviews = None
	for i in products:
		reviews = ReviewRating.objects.filter(product_id=i.id, status=True)

	content = {
		'products':products,
	}

	return render(request,'home.html',content)
