from django import forms
from django.forms import inlineformset_factory
from django.forms import modelformset_factory
from django.forms import formset_factory
from warenwirtschaft.models import Supplier
from warenwirtschaft.models import Delivery
from warenwirtschaft.models import DeliveryUnit
from warenwirtschaft.models import Unload


class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = ['name', 'avv_number', 'street', 'postal_code', 'city', 'phone', 'email', 'note']
        widgets = {
            'note': forms.Textarea(attrs={'rows': 5}),
        }

class DeliveryForm(forms.ModelForm):
    class Meta:
        model = Delivery
        fields = ['supplier', 'delivery_receipt', 'note']
        widgets = {
            'note': forms.Textarea(attrs={'rows': 3}),
        }
        
DeliveryUnitFormSet = inlineformset_factory(
    parent_model=Delivery,
    model=DeliveryUnit,
    fields=['delivery_type', 'material', 'weight'],
    extra=1,
    can_delete=True
)

class DeliveryUnitForm(forms.ModelForm):
    class Meta:
        model = DeliveryUnit
        fields = ['delivery_type', 'material', 'weight']

UnloadFormSet = inlineformset_factory(
    parent_model=DeliveryUnit,
    model=Unload,
    fields=["id", "unload_type", "material", "weight", "purpose", "note"],
    extra=1,
    can_delete=True
)