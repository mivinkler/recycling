from django import forms
from django.forms import modelformset_factory
from warenwirtschaft.models import Recycling, Unload


class UnloadChoiceForm(forms.Form):
    unload = forms.ModelChoiceField(
        queryset=Unload.objects.filter(status=2),
        label="Vorsortierung wählen",
    )


class RecyclingForm(forms.ModelForm):
    class Meta:
        model = Recycling
        fields = [ "material", "box_type", "weight", "note"]


# Formset nur für neue Recycling-Zeilen
NewRecyclingFormSet = modelformset_factory(
    Recycling,
    form=RecyclingForm,
    extra=0,
    can_delete=False,
)

class RecyclingUpdateForm(forms.ModelForm):
    class Meta:
        model = Recycling
        fields = ["material", "box_type", "weight", "note", "status"]
