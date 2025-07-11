from django import forms
from django.forms import inlineformset_factory
from django.forms import modelformset_factory

from warenwirtschaft.models.supplier import Supplier
from warenwirtschaft.models.delivery import Delivery
from warenwirtschaft.models.delivery_unit import DeliveryUnit
from warenwirtschaft.models.unload import Unload
from warenwirtschaft.models.recycling import Recycling
from warenwirtschaft.models.shipping import Shipping
from warenwirtschaft.models.shipping_unit import ShippingUnit
from warenwirtschaft.models.customer import Customer
from warenwirtschaft.models.material import Material
from warenwirtschaft.models.reusable_barcode import ReusableBarcode

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
    fields=['box_type', 'material', 'target', 'material_other', 'weight', 'note'],
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
    fields=['id', 'box_type', 'material', 'weight', 'target', 'note'],
    extra=1,
    can_delete=True
)

# Recycling
class UnloadForm(forms.Form):
    unload = forms.ModelChoiceField(
        queryset=Unload.objects.filter(status=1),
    )

class RecyclingForm(forms.ModelForm):
    selected = forms.BooleanField(
        required=False,
        initial=True,
        label="Ausgewählt"
    )

    class Meta:
        model = Recycling
        fields = ["box_type", "material", "material_other", "weight", "target", "status", "note", "unloads"]
        widgets = {
            "unloads": forms.CheckboxSelectMultiple,
        }

RecyclingFormSet = modelformset_factory(
    Recycling,
    form=RecyclingForm,
    fields=["box_type", "material", "material_other", "weight", "target", "status", "note"],
    extra=1,
    can_delete=True
)

# Shipping
class ShippingForm(forms.ModelForm):
    class Meta:
        model = Shipping
        fields = ['customer', 'certificate', 'transport', 'note']
        widgets = {
            'note': forms.Textarea(attrs={'rows': 3}),
        }
        
ShippingUnitFormSet = inlineformset_factory(
    parent_model=Shipping,
    model=ShippingUnit,
    fields=['recycling', 'box_type', 'material', 'weight', 'status', 'note'],
    extra=1,
    can_delete=True
)


# Customer
class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['name', 'street', 'postal_code', 'city', 'phone', 'email', 'note']
        widgets = {
            'note': forms.Textarea(attrs={'rows': 5}),
        }

# Barcode
class ReusableBarcodeForm(forms.ModelForm):
    class Meta:
        model = ReusableBarcode
        fields = ['supplier', 'delivery_receipt', 'customer', 'box_type', 'material', 'weight', 'area', 'target']


# Material
class MaterialForm(forms.ModelForm):
    class Meta:
        model = Material
        fields = ['name', 'delivery', 'unload', 'recycling']


MaterialFormSet = modelformset_factory(
    Material,
    form=MaterialForm,
    extra=0,
    can_delete=False
)