from django import forms
from django.forms import inlineformset_factory

from warenwirtschaft.models.reusable_barcode import ReusableBarcode

from warenwirtschaft.models.supplier import Supplier
from warenwirtschaft.models.delivery import Delivery
from warenwirtschaft.models.delivery_unit import DeliveryUnit
from warenwirtschaft.models.unload import Unload
from warenwirtschaft.models.recycling import Recycling
from warenwirtschaft.models.shipping import Shipping
from warenwirtschaft.models.shipping_unit import ShippingUnit
from warenwirtschaft.models.customer import Customer

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

RecyclingFormSet = inlineformset_factory(
    parent_model=Unload,
    model=Recycling,
    fields=["id", "box_type", "material", "weight", "target", "note"],
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
    fields=['box_type', 'material', 'weight', 'status', 'note'],
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
        fields = ['box_type', 'material', 'target']
