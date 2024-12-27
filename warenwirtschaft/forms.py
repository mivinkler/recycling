from django import forms
from .models import *


class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = ['avv_number', 'name', 'street', 'postal_code', 'city', 'country', 'phone', 'email', 'note']
        widgets = {
            'avv_number': forms.TextInput(attrs={'placeholder': 'AVV Number'}),
            'name': forms.TextInput(attrs={'class': 'flex-items', 'placeholder': 'Name'}),
            'street': forms.TextInput(attrs={'class': 'flex-items', 'placeholder': 'Address'}),
            'postal_code': forms.TextInput(attrs={'class': 'flex-items', 'placeholder': 'Postal Code'}),
            'city': forms.TextInput(attrs={'class': 'flex-items', 'placeholder': 'City'}),
            'country': forms.TextInput(attrs={'class': 'flex-items', 'placeholder': 'Country'}),
            'phone': forms.TextInput(attrs={'class': 'flex-items', 'placeholder': 'Phone'}),
            'email': forms.EmailInput(attrs={'class': 'flex-items', 'placeholder': 'Email'}),
            'note': forms.Textarea(attrs={'class': 'flex-items', 'rows': 4, 'placeholder': 'Note'}),
        }