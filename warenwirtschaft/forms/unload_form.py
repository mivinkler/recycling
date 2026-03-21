from django import forms

from warenwirtschaft.models import Material, Unload
from warenwirtschaft.models_common.choices import StatusChoices


UNLOAD_FORM_DEFAULT_STATUS = StatusChoices.WARTET_AUF_ZERLEGUNG
UNLOAD_FORM_STATUS_CHOICES = [
    (StatusChoices.WARTET_AUF_ZERLEGUNG, "Wartet auf Zerlegung"),
    (StatusChoices.WARTET_AUF_ABHOLUNG, "Wartet auf Abholung"),
]


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
        self.fields["material"].queryset = Material.for_section(
            "unload",
            include=self.instance.material_id,
        )
        self.fields["status"].choices = UNLOAD_FORM_STATUS_CHOICES
        if not self.instance.pk:
            self.fields["status"].initial = UNLOAD_FORM_DEFAULT_STATUS
