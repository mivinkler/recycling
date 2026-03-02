from django import forms

from warenwirtschaft.models.halle_zwei import HalleZwei
from warenwirtschaft.models_common.choices import StatusChoices


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

        allowed = {
            StatusChoices.WARTET_AUF_ABHOLUNG,
        }

        # Nur erlaubte Statuswerte im Dropdown anzeigen
        self.fields["status"].choices = [
            (value, label)
            for value, label in self.fields["status"].choices
            if value in allowed
        ]

        # Standardwert für neue Units
        if not self.instance.pk:
            self.fields["status"].initial = StatusChoices.AKTIV_IN_HALLE_ZWEI