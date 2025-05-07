from django import forms
from django.forms import inlineformset_factory
from django.forms import modelformset_factory
from django.forms import formset_factory
from warenwirtschaft.models import Supplier
from warenwirtschaft.models import Delivery
from warenwirtschaft.models import DeliveryUnit
from warenwirtschaft.models import Unload
from warenwirtschaft.models import Recycling


# Supplier
class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = ['name', 'avv_number', 'street', 'postal_code', 'city', 'phone', 'email', 'note']
        widgets = {
            'note': forms.Textarea(attrs={'rows': 5}),
        }


# Delivery
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


# Unload
class DeliveryUnitForm(forms.Form):
    delivery_unit = forms.ModelChoiceField(
        queryset=DeliveryUnit.objects.filter(status=1),
        label="Liefereinheit"
    )

UnloadFormSet = inlineformset_factory(
    parent_model=DeliveryUnit,
    model=Unload,
    fields=["id", "unload_type", "material", "weight", "purpose", "note"],
    extra=1,
    can_delete=True
)

# Recycling
class UnloadForm(forms.Form):
    unload = forms.ModelChoiceField(
        queryset=Unload.objects.filter(status=1),
    )

RecyclingFormSet = inlineformset_factory(
    parent_model=Unload,
    model=Recycling,
    fields=["id", "box_type", "material", "weight", "target", "note"],
    extra=1,
    can_delete=True
)