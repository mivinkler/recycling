from django import forms

from warenwirtschaft.models.customer import Customer
from warenwirtschaft.models.delivery_unit import DeliveryUnit


class DeliveryForm(forms.ModelForm):
    customer = forms.ModelChoiceField(
        queryset=Customer.objects.order_by("name"),
        required=True,
        label="Lieferant",
    )

    delivery_receipt = forms.CharField(
        required=False,
        label="Lieferschein",
    )

    class Meta:
        model = DeliveryUnit
        fields = ["material", "box_type", "weight", "note"]