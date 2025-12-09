# warenwirtschaft/forms/unload_form.py
from django import forms
from django.forms import modelformset_factory
from warenwirtschaft.models import Unload, DeliveryUnit


class UnloadForm(forms.ModelForm):
    """
    Formular für neue Vorsortierungs-Wagen.
    """

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


class ExistingEditForm(forms.ModelForm):
    """
    Formular für bestehende Wagen inkl. Auswahl-Flag.
    """

    selected = forms.BooleanField(
        required=False,
        label="verknüpft",
    )

    def __init__(self, *args, **kwargs):
        selected_initial = kwargs.pop("selected_initial", False)
        super().__init__(*args, **kwargs)
        self.fields["selected"].initial = selected_initial

    class Meta:
        model = Unload
        fields = ["status", "weight", "note"]
        labels = {
            "status": "Status",
            "weight": "Gewicht",
            "note": "Anmerkung",
        }


UnloadFormSet = modelformset_factory(
    Unload,
    form=UnloadForm,
    extra=1,
    can_delete=False,
)


ExistingEditFormSet = modelformset_factory(
    Unload,
    form=ExistingEditForm,
    extra=0,
    can_delete=False,
)
