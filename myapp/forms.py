from django import forms
from .models import Product
from django.contrib.auth.models import User

class ProductForm(forms.ModelForm):
    class Meta:
        model=Product
        fields=['name','description','price','file']

from django.contrib.auth.forms import UserCreationForm

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(label='Email')
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ['username', 'email', 'password1', 'password2']

