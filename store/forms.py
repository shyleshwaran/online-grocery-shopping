from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from .models import Order


USER = get_user_model()

class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = USER
        fields = ( 'username', 'email', 'password1', 'password2')

class CheckoutForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['full_name', 'address', 'city', 'pincode', 'phone']
        widgets = { 
            'address': forms.Textarea(attrs={'rows': 2}),
            
            }

