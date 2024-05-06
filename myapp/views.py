from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse, HttpResponseNotFound
from django.shortcuts import get_object_or_404, reverse

from .models import Product,OrderDetails

import json
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt

from .models import Product
from .forms import ProductForm, UserRegistrationForm

from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required

from django.db.models import Sum
import datetime

def welcome(request):
    return render(request, "myapp/welcome.html")
def index(request):
    products = Product.objects.all()
    context={
        "products":products
    }
    return render(request, "myapp/index.html",context)

def details(request, id):
    product = Product.objects.get(id=id)
    context={
        "product":product
    }
    return render(request, "myapp/details.html",context)


@login_required
def create_product(request):
    if request.method == 'POST':
        product_form = ProductForm(request.POST, request.FILES or None)
        if product_form.is_valid():
            new_product= product_form.save(commit=False)
            new_product.seller= request.user
            new_product.save()
            return redirect('myapp:index')
    product_form = ProductForm()
    return render(request, 'myapp/create_product.html', {'product_form': product_form})
        

@login_required
def edit_product(request, id):
    product = Product.objects.get(id=id) 
    if product.seller != request.user:
        return redirect("myapp:invalid")
    if request.method == 'POST':
        product_form = ProductForm(request.POST, request.FILES or None, instance=product)
        if product_form.is_valid():
            new_product= product_form.save()
            return redirect('myapp:index')
    product_form = ProductForm(instance=product)
    return render(request, 'myapp/edit_product.html', {'product_form': product_form, 'product': product})

@login_required
def delete_product(request, id):
    product = Product.objects.get(id=id)
    if product.seller != request.user:
        return redirect("myapp:invalid")
    if request.method == 'POST':
        product.delete()
        return redirect('myapp:index')
    return render(request, 'myapp/delete_product.html', {'product': product})

@login_required
def dashboard(request):
    products = Product.objects.filter(seller=request.user)
    context = {
        'products': products
    }
    return render(request, 'myapp/dashboard.html', context)

def register(request):
    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST)
        if user_form.is_valid():
            user_form.save()
            return redirect('myapp:index')
    else:
        user_form = UserRegistrationForm()
    return render(request, 'myapp/register.html', {'user_form': user_form})
def logout_view(request):
    logout(request)
    return render(request, "myapp/logout.html")

def invalid_view(request):
    return render(request, "myapp/invalid.html")

import paypalrestsdk
from django.conf import settings
from django.shortcuts import render, redirect
from django.urls import reverse

paypalrestsdk.configure({
    "mode": "sandbox",  # Change to "live" for production
    "client_id": settings.PAYPAL_CLIENT_ID,
    "client_secret": settings.PAYPAL_SECRET,
})
def create_payment(request):
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        email= request.POST.get('user_email')
        product = Product.objects.get(id=product_id)
        description = f"Product ID: {product_id}, Email: {email}"
        payment = paypalrestsdk.Payment({
            "intent": "sale",
            "payer": {
                "payment_method": "paypal",
            },
            "redirect_urls": {
                "return_url": request.build_absolute_uri(reverse('myapp:execute_payment')),
                "cancel_url": request.build_absolute_uri(reverse('myapp:payment_failed')),
            },
            "transactions": [
                {
                    "amount": {
                        "total": str(product.price),  # Convert price to string
                        "currency": "USD",
                    },
                    "description": f"{description}",
                }
            ],
        })
        if payment.create():
            return redirect(payment.links[1].href)  # Redirect to PayPal for payment
        else:
            return render(request, 'myapp/payment_failed.html')
    else:
        return redirect('myapp:payment_failed')

def execute_payment(request):
    payment_id = request.GET.get('paymentId')
    payer_id = request.GET.get('PayerID')
    payment = paypalrestsdk.Payment.find(payment_id)

    description= payment.transactions[0].description
    description_parts = description.split(", ")
    product_id = None
    email = None
    for part in description_parts:
        if part.startswith("Product ID"):
            product_id = part.split(": ")[1]
        elif part.startswith("Email"):
            email = part.split(": ")[1]
    print("Product ID:", product_id)
    print("Email:", email)
    print(payment)

    if payment.execute({"payer_id": payer_id}):
        order = OrderDetails()
        product= Product.objects.get(id=product_id)
        order.customer_email = email
        order.product = product
        order.amount = int(product.price)
        order.payment_id = payment.id
        # update the total sales amount you have to add the current amount to respective product totsl_sales amount
        product.total_sales_amount = product.total_sales_amount + order.amount
        product.total_sales = product.total_sales + 1
        # update the number of sales for this add 1 to the current number of sales
        order.has_paid=True
        order.save()
        product.save()
        return render(request, 'myapp/payment_success.html',{'product_id': product_id})
    else:
        return render(request, 'myapp/payment_failed.html')

@login_required
def payment_checkout(request,id):
    product = Product.objects.get(id=id)
    context={
        "product":product
    }
    return render(request, 'myapp/checkout.html',context)

def payment_failed(request):
    return render(request, 'myapp/payment_failed.html')

@login_required
def my_purchases(request):
    orders = OrderDetails.objects.filter(customer_email=request.user.email)
    return render(request, 'myapp/purchases.html',{'orders':orders})

@login_required
def sales(request):
    orders = OrderDetails.objects.filter(product__seller=request.user)
    total_sales = orders.aggregate(Sum('amount'))
    print(total_sales)
    
    #365 day sales sum
    last_year = datetime.date.today() - datetime.timedelta(days=365)
    data = OrderDetails.objects.filter(product__seller=request.user,created_on__gt=last_year)
    yearly_sales = data.aggregate(Sum('amount'))
    
    #30 day sales sum
    last_month = datetime.date.today() - datetime.timedelta(days=30)
    data = OrderDetails.objects.filter(product__seller=request.user,created_on__gt=last_month)
    monthly_sales = data.aggregate(Sum('amount'))
    
    #7 day sales sum
    last_week = datetime.date.today() - datetime.timedelta(days=7)
    data = OrderDetails.objects.filter(product__seller=request.user,created_on__gt=last_week)
    weekly_sales = data.aggregate(Sum('amount'))
    
    #Everday sum for the past 30 days
    daily_sales_sums = OrderDetails.objects.filter(product__seller=request.user).values('created_on__date').order_by('created_on__date').annotate(sum=Sum('amount'))
    
    
    
    product_sales_sums = OrderDetails.objects.filter(product__seller=request.user).values('product__name').order_by('product__name').annotate(sum=Sum('amount'))
    print(product_sales_sums)

    return render(request, 'myapp/sales.html',{'total_sales':total_sales,'yearly_sales':yearly_sales,'monthly_sales':monthly_sales,'weekly_sales':weekly_sales,'daily_sales_sums':daily_sales_sums,'product_sales_sums':product_sales_sums})
