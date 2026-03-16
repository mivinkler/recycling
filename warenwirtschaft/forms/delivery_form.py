from django import forms
from warenwirtschaft.models import Delivery, DeliveryUnit, Material


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
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["material"].queryset = Material.for_section(
            "delivery",
            include=self.instance.material_id,
        )

    class Meta:
        model = DeliveryUnit
        fields = ["material", "box_type", "weight", "note"]
