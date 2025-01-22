from django import forms
from django.forms import modelformset_factory
from .models import *


class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = ['name', 'avv_number', 'street', 'postal_code', 'city', 'phone', 'email', 'note']
        widgets = {
            'note': forms.Textarea(attrs={'rows': 4}),
        }

class DeliveryForm(forms.ModelForm):
    class Meta:
        model = Delivery
        fields = ['weight', 'units', 'delivery_receipt', 'delivery_date']
        widgets = {
            'note': forms.Textarea(attrs={'rows': 4}),
        }

class UnloadingForm(forms.ModelForm):
    class Meta:
        model = Unloading
        fields = ['unload_type', 'device', 'weight', 'purpose', 'note']
        widgets = {
            'note': forms.Textarea(attrs={'rows': 2}),
            'weight': forms.NumberInput(attrs={'min': 0, 'step': 0.1}),
        }

UnloadingFormSet = modelformset_factory(
    Unloading,
    form=UnloadingForm,
    extra=1,
)