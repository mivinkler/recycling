from django import forms
from warenwirtschaft.models import Delivery, DeliveryUnit, Material
from warenwirtschaft.models_common.choices import StatusChoices


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
    ALLOWED_STATUSES = {
        StatusChoices.WARTET_AUF_VORSORTIERUNG,
        StatusChoices.WARTET_AUF_HALLE_ZWEI,
    }

    def __init__(self, *args, **kwargs):
        form_data = kwargs.get("data")
        if form_data is not None and not form_data.get("status"):
            form_data = form_data.copy()
            form_data["status"] = str(StatusChoices.WARTET_AUF_VORSORTIERUNG)
            kwargs["data"] = form_data

        super().__init__(*args, **kwargs)
        self.fields["material"].queryset = Material.for_section(
            "delivery",
            include=self.instance.material_id,
        )
        allowed_statuses = set(self.ALLOWED_STATUSES)
        if self.instance.pk and self.instance.status is not None:
            allowed_statuses.add(self.instance.status)

        self.fields["status"].choices = [
            (value, label)
            for value, label in self.fields["status"].choices
            if value in allowed_statuses
        ]
        if not self.instance.pk:
            self.fields["status"].initial = StatusChoices.WARTET_AUF_VORSORTIERUNG

    class Meta:
        model = DeliveryUnit
        fields = ["material", "box_type", "status", "weight", "note"]
