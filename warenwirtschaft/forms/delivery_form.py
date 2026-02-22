from django import forms
from warenwirtschaft.models import Delivery, DeliveryUnit

class DeliveryForm(forms.ModelForm):
    class Meta:
        model = Delivery
        fields = ["customer", "delivery_receipt"]

class DeliveryUnitForm(forms.ModelForm):
    class Meta:
        model = DeliveryUnit
        fields = ["material", "box_type", "weight", "note"]