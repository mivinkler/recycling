from django import forms
from django.forms import inlineformset_factory
from warenwirtschaft.models import Supplier
from warenwirtschaft.models import Delivery
from warenwirtschaft.models import DeliveryUnit
from warenwirtschaft.models import Unload


class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = ['name', 'avv_number', 'street', 'postal_code', 'city', 'phone', 'email', 'note']
        widgets = {
            'note': forms.Textarea(attrs={'rows': 3}),
        }

class DeliveryForm(forms.ModelForm):
    class Meta:
        model = Delivery
        fields = ['supplier', 'delivery_receipt', 'note']
        widgets = {
            'note': forms.Textarea(attrs={'rows': 3}),
        }
    
DeliveryUnitFormSet = inlineformset_factory(
    Delivery,
    DeliveryUnit,
    fields=['delivery_type', 'material', 'weight'],
    extra=0,
    can_delete=True
)

class UnloadForm(forms.ModelForm):
    class Meta:
        model = Unload
        fields = ['unload_type', 'material', 'weight', 'purpose', 'note']
        widgets = {
            'note': forms.Textarea(attrs={'rows': 3}),
        }
# unloadFormSet = modelformset_factory(
#     unload,
#     form=unloadForm,
#     extra=1,
# )