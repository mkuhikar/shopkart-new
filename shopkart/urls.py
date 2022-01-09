
from django.contrib import admin
from django.urls import path, include
from . import views
from django.conf.urls.static import static
from . import settings

urlpatterns = [
    path('admin/', include('admin_honeypot.urls',namespace='admin_honeypot')),
    path('shopkartadmin/', admin.site.urls),
    path('', views.home, name='home'),
    path('store/',include('products.urls')),
    path('cart/',include('carts.urls')),
    path('accounts/', include('accounts.urls')),
    path('orders/', include('orders.urls')),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
