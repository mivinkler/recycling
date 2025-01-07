from django import forms
from .models import *


class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = ['name', 'avv_number', 'street', 'postal_code', 'city', 'phone', 'email', 'note']
        widgets = {
            'note': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Note'}),
        }

class DeliveryForm(forms.ModelForm):
    class Meta:
        model = Delivery
        fields = ['weight', 'units', 'delivery_receipt', 'delivery_date']
        widgets = {
            'note': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Note'}),
        }