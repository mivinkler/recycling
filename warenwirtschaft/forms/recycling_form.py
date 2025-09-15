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

# extra=0, sodass ein leeres Formset gültig ist, wenn der Benutzer nichts hinzugefügt hat
RecyclingFormSet = modelformset_factory(
    Recycling,
    form=RecyclingForm,
    extra=1,
    can_delete=True,
    validate_min=False,
    validate_max=False,
)
