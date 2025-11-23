from django import forms
from warenwirtschaft.models import Unload
from warenwirtschaft.models.recycling import Recycling


class DailyWeightForm(forms.Form):
    recycling_status = forms.ChoiceField(
        choices=Recycling.STATUS_CHOICES,
        required=False,
        label="Status",
    )

    unload_status = forms.ChoiceField(
        choices=Unload.STATUS_CHOICES,
        required=False,
        label="Status",
    )

    new_weight = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False,
        label="Neues Gewicht",
    )

    new_note = forms.CharField(
        required=False,
        label="Neue Anmerkung",
        widget=forms.TextInput(),
    )
