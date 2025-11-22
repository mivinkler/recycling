from django import forms
from warenwirtschaft.models import Unload, Recycling


class DeviceCheckForm(forms.Form):
    # "unload-12" или "recycling-5"
    container = forms.ChoiceField(
        widget=forms.RadioSelect,
        label="Behälter auswählen",
    )

    weight = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False,
        label="Gewicht (nach Prüfung)"
    )

    note = forms.CharField(
        max_length=255,
        required=False,
        label="Anmerkung",
        widget=forms.Textarea(attrs={"rows": 3}),
    )

    def __init__(self, *args, **kwargs):
        unload_qs = kwargs.pop("unload_qs", Unload.objects.none())
        recycling_qs = kwargs.pop("recycling_qs", Recycling.objects.none())
        super().__init__(*args, **kwargs)

        # Liste der Behälter aufbauen
        choices = []

        for u in unload_qs:
            value = f"unload-{u.id}"
            label = f"Unload #{u.id} – {u.get_box_type_display()} – {u.weight} kg"
            choices.append((value, label))

        for r in recycling_qs:
            value = f"recycling-{r.id}"
            label = f"Recycling #{r.id} – {r.get_box_type_display()} – {r.weight} kg"
            choices.append((value, label))

        self.fields["container"].choices = choices
