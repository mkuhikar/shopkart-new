from django.contrib import admin
from .models import Payment, Order, OrderProduct

# Register your models here.

class OrderProductInline(admin.TabularInline):
    model = OrderProduct
    readonly_fields = ('payment','user','product','quantity','product_price','ordered')
    extra = 0

class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number','full_name','phone','city','email','order_total','status','is_ordered','created_at']
    list_filter = ['status','is_ordered']
    search_fields = ['is_ordered','first_name','last_name','email']
    list_per_page = 20
    inlines = [OrderProductInline]
    prepopulated_fields = {'slug':('order_number',)}

admin.site.register(Order, OrderAdmin)
admin.site.register(Payment)
admin.site.register(OrderProduct)
