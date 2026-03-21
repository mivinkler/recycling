from django import forms

from warenwirtschaft.models.halle_zwei import HalleZwei
from warenwirtschaft.models_common.choices import StatusChoices


HALLE_ZWEI_FORM_DEFAULT_STATUS = StatusChoices.AKTIV_IN_HALLE_ZWEI
HALLE_ZWEI_FORM_STATUS_CHOICES = [
    (StatusChoices.WARTET_AUF_ABHOLUNG, "Wartet auf Abholung"),
]


class HalleZweiForm(forms.ModelForm):
    class Meta:
        model = HalleZwei
        fields = ["status", "note"]
        labels = {
            "status": "Status",
            "note": "Anmerkung",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["status"].choices = HALLE_ZWEI_FORM_STATUS_CHOICES
        if not self.instance.pk:
            self.fields["status"].initial = HALLE_ZWEI_FORM_DEFAULT_STATUS
