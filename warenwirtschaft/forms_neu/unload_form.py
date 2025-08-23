from django import forms
from django.forms import modelformset_factory
from warenwirtschaft.models import Unload, DeliveryUnit


class DeliveryUnitChoiceForm(forms.Form):
    delivery_unit = forms.ModelChoiceField(
        queryset=DeliveryUnit.objects.filter(status=1),
        label="Liefereinheit"
    )


class UnloadForm(forms.ModelForm):
    class Meta:
        model = Unload
        fields = ['box_type', 'material', 'weight', 'status', 'note']


# DE: Immer 1 leere Zeile im Formset für neue Unloads
UnloadFormSet = modelformset_factory(
    Unload,
    form=UnloadForm,
    extra=1,
    can_delete=True,
    validate_min=False,
    validate_max=False,
)
