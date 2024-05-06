from django.contrib import admin
from .models import Product,OrderDetails

admin.site.register(Product)
admin.site.register(OrderDetails)