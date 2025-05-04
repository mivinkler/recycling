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
    Delivery,
    DeliveryUnit,
    fields=['delivery_type', 'material', 'weight'],
    extra=1,
    can_delete=True
)

class UnloadDeliveryUnitForm(forms.Form):
    delivery_unit = forms.ModelChoiceField(
        queryset=DeliveryUnit.objects.filter(status=1),
        label="Liefereinheit"
    )

class UnloadForm(forms.ModelForm):
    class Meta:
        model = Unload
        fields = ['unload_type', 'material', 'weight', 'purpose', 'note']

UnloadFormSet = inlineformset_factory(
    parent_model=DeliveryUnit,
    model=Unload,
    fields=["unload_type", "material", "weight", "purpose", "note"],
    extra=1,
    can_delete=True
)