from django.db import models
from django.contrib.auth.models import User

class Product(models.Model):
    CATEGORY_CHOICES = [
        ('Goods', 'Goods'),
        ('Services', 'Services'),
    ]
    seller= models.ForeignKey(User, on_delete=models.CASCADE,default=1)
    name=models.CharField(max_length=200)
    description=models.CharField(max_length=200)
    price=models.FloatField()
    file=models.FileField(upload_to="uploads")
    total_sales_amount = models.IntegerField(default=0)
    total_sales = models.IntegerField(default=0)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='Goods')


    def __str__(self):
        return self.name
    
class OrderDetails(models.Model):
    customer_email=models.EmailField(max_length=200)
    product=models.ForeignKey(Product,on_delete=models.CASCADE)
    amount=models.IntegerField()
    payment_id=models.CharField(max_length=500,blank=True,null=True)
    has_paid=models.BooleanField(default=False)
    created_on=models.DateTimeField(auto_now_add=True)
    updated_on=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.customer_email