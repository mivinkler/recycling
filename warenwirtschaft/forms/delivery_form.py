from django import forms
from warenwirtschaft.models import Delivery, DeliveryUnit, Material
from warenwirtschaft.models_common.choices import StatusChoices


DELIVERY_FORM_B2B_CHOICES = [
    (False, "Nein"),
    (True, "Ja"),
]

DELIVERY_UNIT_FORM_STATUS_CHOICES = [
    (StatusChoices.WARTET_AUF_VORSORTIERUNG, "Wartet auf Vorsortierung"),
    (StatusChoices.WARTET_AUF_HALLE_ZWEI, "Wartet auf Halle Zwei"),
]

DELIVERY_UNIT_DEFAULT_STATUS = StatusChoices.WARTET_AUF_VORSORTIERUNG
DELIVERY_UNIT_ALLOWED_STATUSES = {
    value for value, _ in DELIVERY_UNIT_FORM_STATUS_CHOICES
}


class DeliveryForm(forms.ModelForm):
    b2b = forms.ChoiceField(
        choices=DELIVERY_FORM_B2B_CHOICES,
        widget=forms.Select,
    )

    class Meta:
        model = Delivery
        fields = ["customer", "delivery_receipt", "b2b"]


class DeliveryUnitForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        form_data = kwargs.get("data")
        if form_data is not None and not form_data.get("status"):
            form_data = form_data.copy()
            form_data["status"] = str(DELIVERY_UNIT_DEFAULT_STATUS)
            kwargs["data"] = form_data

        super().__init__(*args, **kwargs)
        self.fields["material"].queryset = Material.for_section(
            "delivery",
            include=self.instance.material_id,
        )
        self.fields["status"].choices = DELIVERY_UNIT_FORM_STATUS_CHOICES
        current_status = self.instance.status
        if (
            self.instance.pk
            and current_status is not None
            and current_status not in DELIVERY_UNIT_ALLOWED_STATUSES
        ):
            self.fields["status"].choices = [
                *DELIVERY_UNIT_FORM_STATUS_CHOICES,
                (current_status, self.instance.get_status_display()),
            ]
        if not self.instance.pk:
            self.fields["status"].initial = DELIVERY_UNIT_DEFAULT_STATUS

    class Meta:
        model = DeliveryUnit
        fields = ["material", "box_type", "status", "weight", "note"]
