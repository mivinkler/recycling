from django import forms
from django.forms import inlineformset_factory
from warenwirtschaft.models import *


class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = ['name', 'avv_number', 'street', 'postal_code', 'city', 'phone', 'email', 'note']

class DeliveryForm(forms.ModelForm):
    class Meta:
        model = Delivery
        fields = ['supplier', 'delivery_receipt', 'note' ]
    
DeliveryUnitFormSet = inlineformset_factory(
    Delivery,
    DeliveryUnit,
    fields=['delivery_type', 'material', 'weight'],
    extra=1,
    can_delete=True
)

class UnloadForm(forms.ModelForm):
    class Meta:
        model = Unload
        fields = ['unload_type', 'material', 'weight', 'purpose', 'note']

# unloadFormSet = modelformset_factory(
#     unload,
#     form=unloadForm,
#     extra=1,
# )