from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

from django.views.generic import ListView
from .models import Product

app_name = 'myapp'
urlpatterns = [
    # path('', views.index, name='index'),
    path('', ListView.as_view(queryset=Product.objects.all(), template_name='myapp/index.html', paginate_by=6), name='index'),
    path('product/<int:id>/', views.details, name='details'),
    
    path('createproduct/', views.create_product, name='createproduct'),
    path('editproduct/<int:id>/', views.edit_product, name='editproduct'),
    path('deleteproduct/<int:id>/', views.delete_product, name='deleteproduct'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='myapp/login.html'), name='login'),
    path('logout/',  views.logout_view, name='logout'),
    path('invalid/', views.invalid_view, name='invalid'),
    
    path('checkout/<int:id>/', views.payment_checkout, name='checkout_payment'),
    path('create_payment/', views.create_payment, name='create_payment'),
    path('execute_payment/', views.execute_payment, name='execute_payment'),
    path('payment_failed/', views.payment_failed, name='payment_failed'),

    path('purchases/',views.my_purchases,name='purchases'),
    path('sales/',views.sales,name='sales'),
]


# .\env\Scripts\activate