from django import forms

from warenwirtschaft.models import Unload
from warenwirtschaft.models_common.choices import StatusChoices


class UnloadForm(forms.ModelForm):
    class Meta:
        model = Unload
        fields = ["box_type", "material", "weight", "status", "note"]
        labels = {
            "box_type": "Behälter",
            "material": "Material",
            "weight": "Gewicht",
            "status": "Status",
            "note": "Anmerkung",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        allowed = {
            StatusChoices.WARTET_AUF_ZERLEGUNG,
            StatusChoices.WARTET_AUF_HALLE_ZWEI,
            StatusChoices.WARTET_AUF_ABHOLUNG,
        }

        # Nur erlaubte Statuswerte im Dropdown anzeigen
        self.fields["status"].choices = [
            (value, label)
            for value, label in self.fields["status"].choices
            if value in allowed
        ]

        # Optional: Standardwert für neue Unloads
        if not self.instance.pk:
            self.fields["status"].initial = StatusChoices.AKTIV_IN_VORSORTIERUNG