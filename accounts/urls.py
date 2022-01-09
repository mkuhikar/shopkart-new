from django.urls import path
from . import views

urlpatterns = [
    path('register/',views.register, name='register'),
    path('login/',views.login, name='login'),
    path('logout/',views.logout, name='logout'),
    path('activate/<uidb64>/<token>/', views.activate, name='activate'),
    path('dashboard/',views.dashboard,name='dashboard'),
    path('',views.dashboard,name='dashboard'),
    path('forgotPassword/',views.forgotPassword,name='forgotPassword'),
    path('reset/<uidb64>/<token>/', views.reset, name='reset'),
    path('resetPassword', views.resetPassword, name='resetPassword'),

    path('my_orders', views.my_orders, name='my_orders'),
    path('edit_profile', views.edit_profile, name='edit_profile'),
    path('change_password/', views.change_password, name='change_password'),
    path('order_detail/<int:order_id>/', views.order_detail, name='order_detail'),

    path('pdffile/<int:order_number>',views.generate_obj_pdf, name='receipt_download'),
    path('user/orderreceipt/<int:order_number>/',views.order_receipt, name='order_receipt'),
    path('user/sendreceipt/<int:order_number>/',views.send_receipt, name='send_receipt'),
    path('delay',views.delayprogram)



]
