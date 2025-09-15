from django import forms
from django.forms import modelformset_factory
from warenwirtschaft.models import Recycling, Unload


class UnloadChoiceForm(forms.Form):
    unload = forms.ModelChoiceField(
        queryset=Unload.objects.filter(status=1),
        label="Vorsortierung wählen"
    )


class RecyclingForm(forms.ModelForm):
    class Meta:
        model = Recycling
        fields = ["box_type", "material", "status", "weight"]


# ---- Form für die Auswahl bestehender aktiver Recycling-Objekte ----
class ExistingRecyclingField(forms.ModelMultipleChoiceField):
    # Label je Zeile (nur für Debug/Fallback, wir rendern manuell im Template)
    def label_from_instance(self, obj):
        return f"{obj.material} — {obj.get_box_type_display()} — {obj.get_status_display()} — {obj.weight or 0}"


class ExistingRecyclingForm(forms.Form):
    # queryset wird im View gesetzt/benutzt; required=False erlaubt „alles abwählen“
    existing = ExistingRecyclingField(
        queryset=Recycling.objects.none(),
        required=False,
        widget=forms.CheckboxSelectMultiple
    )


# ---- Formset NUR für NEUE Zeilen ----
NewRecyclingFormSet = modelformset_factory(
    Recycling,
    form=RecyclingForm,
    extra=0,          # gültig auch ohne neue Zeilen
    can_delete=False,
    validate_min=False,
    validate_max=False,
)
