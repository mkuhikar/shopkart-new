from django.db import models
from category.models import Category
from django.urls import reverse
from accounts.models import Account
from django.db.models import Avg, Count


# Create your models here.

class Product(models.Model):
    product_name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True)
    price = models.IntegerField()
    description = models.TextField(max_length=250, blank=True)
    stock = models.IntegerField()
    image = models.ImageField(upload_to='products/images')
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    is_available = models.BooleanField(default=True)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.product_name

    def get_url(self):
        return reverse ('product_detail',args=[self.category.slug,self.slug])

    def averageReview(self):
        reviews = ReviewRating.objects.filter(product=self, status=True).aggregate(average=Avg('rating'))
        avg = 0
        if reviews['average'] is not None:
            avg = float(reviews['average'])
        return avg
    def reviewCount(self):
        reviewcounts = ReviewRating.objects.filter(product=self, status=True).aggregate(count=Count('rating'))
        count = 0
        if reviewcounts['count'] is not None:
            count = int(reviewcounts['count'])
        return count



class VariationManager(models.Manager):
    def colors(self):
        return super(VariationManager, self).filter(variation_category='color',is_active=True)

    def sizes(self):
        return super(VariationManager,self).filter(variation_category='size', is_active=True)

variation_category_choice = (
('color','color'),
('size','size'),
)

class Variation(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variation_category = models.CharField(max_length=50, choices=variation_category_choice)
    variation_value = models.CharField(max_length=100)
    is_active=models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now=True)

    objects = VariationManager()

    def __str__(self):
        return self.variation_value

class ReviewRating(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    subject = models.CharField(max_length=100, blank=True)
    review = models.TextField(max_length=500, blank=True)
    rating = models.FloatField()
    ip = models.CharField(max_length=20,blank=True)
    status = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True) #adds date on creation
    updated_at = models.DateTimeField(auto_now=True) #updates date everytime

    def __str__(self):
        return self.subject

class ProductGallery(models.Model):
    product = models.ForeignKey(Product,on_delete=models.CASCADE)
    image = models.ImageField(upload_to='products/images')

    def __str__(self):
        return self.product.product_name
        
