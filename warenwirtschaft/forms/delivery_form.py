from django import forms
from warenwirtschaft.models import Delivery, DeliveryUnit


class DeliveryForm(forms.ModelForm):

    # Boolean-Feld mit Select-Widget
    b2b = forms.ChoiceField(
        choices=[(False, "Nein"), (True, "Ja")],
        widget=forms.Select
    )

    class Meta:
        model = Delivery
        fields = ["customer", "delivery_receipt", "b2b"]


class DeliveryUnitForm(forms.ModelForm):
    class Meta:
        model = DeliveryUnit
        fields = ["material", "box_type", "weight", "note"]
