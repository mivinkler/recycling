from django import forms
from django.forms import modelformset_factory
from warenwirtschaft.models import Unload, DeliveryUnit

class DeliveryUnitForm(forms.Form):
    delivery_units = forms.ModelMultipleChoiceField(
        queryset=DeliveryUnit.objects.filter(status=1),
        label="Liefereinheiten",
        widget=forms.SelectMultiple
    )

class UnloadForm(forms.ModelForm):
    class Meta:
        model = Unload
        fields = ['box_type', 'material', 'weight', 'status', 'note', 'delivery_units']
        widgets = {
            # DE: Für bessere Mehrfachauswahl:
            'delivery_units': forms.SelectMultiple,
        }
        labels = {
            'delivery_units': 'Liefereinheiten',
        }

# DE: Einfaches Formular für bestehende Unloads – nur Status + Gewicht,
#     beide Felder sind initial deaktiviert; werden per JS aktiviert.
class ExistingEditForm(forms.ModelForm):
    class Meta:
        model = Unload
        fields = ['status', 'weight']
        widgets = {
            'status': forms.Select(attrs={
                'class': 'editable-field',
                'disabled': 'disabled',
            }),
            'weight': forms.NumberInput(attrs={
                'class': 'editable-field',
                'step': '0.01',
                'inputmode': 'decimal',
                'disabled': 'disabled',
            }),
        }
        labels = {
            'status': 'Status',
            'weight': 'Gewicht',
        }

UnloadFormSet = modelformset_factory(
    Unload,
    form=UnloadForm,
    extra=1,
    can_delete=True,
    validate_min=False,
    validate_max=False,
)

ExistingEditFormSet = modelformset_factory(
    Unload,
    form=ExistingEditForm,
    extra=0,
    can_delete=False,
)
