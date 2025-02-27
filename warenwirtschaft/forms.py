from django import forms
from django.forms import modelformset_factory
from .models import *
from warenwirtschaft.models import Unload


class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = ['name', 'avv_number', 'street', 'postal_code', 'city', 'phone', 'email', 'note']

class DeliveryForm(forms.ModelForm):
    class Meta:
        model = Delivery
        fields = ['total_weight', 'delivery_receipt']

class UnloadForm(forms.ModelForm):
    class Meta:
        model = Unload
        fields = ['unload_type', 'device', 'weight', 'purpose', 'note']

# unloadFormSet = modelformset_factory(
#     unload,
#     form=unloadForm,
#     extra=1,
# )