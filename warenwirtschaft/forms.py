from django import forms
from django.forms import modelformset_factory
from .models import *


class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = ['name', 'avv_number', 'street', 'postal_code', 'city', 'phone', 'email', 'note']

class DeliveryForm(forms.ModelForm):
    class Meta:
        model = Delivery
        fields = ['weight', 'units', 'delivery_receipt', 'delivery_date']

class unloadForm(forms.ModelForm):
    class Meta:
        model = unload
        fields = ['unload_type', 'device', 'weight', 'purpose', 'note']

unloadFormSet = modelformset_factory(
    unload,
    form=unloadForm,
    extra=1,
)