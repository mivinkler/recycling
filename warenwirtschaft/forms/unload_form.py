# warenwirtschaft/forms/unload_form.py
from django import forms
from django.forms import modelformset_factory
from warenwirtschaft.models import Unload, DeliveryUnit

class DeliveryUnitForm(forms.Form):
    delivery_unit = forms.ModelChoiceField(
        queryset=DeliveryUnit.objects.filter(status=1),
        label="Liefereinheit",
        widget=forms.Select
    )

class UnloadForm(forms.ModelForm):
    class Meta:
        model = Unload
        fields = ['box_type', 'material', 'weight', 'status', 'note']
        labels = {
            'weight': 'Gewicht',
            'status': 'Status',
        }

class ExistingEditForm(forms.ModelForm):
    # Anzeige-/Steuerfeld für M2M-Auswahl (wird NICHT gespeichert)
    selected = forms.BooleanField(required=False, label="verknüpft")

    def __init__(self, *args, **kwargs):
        # Initialwert von außen übergeben (aus DB)
        selected_initial = kwargs.pop("selected_initial", False)
        super().__init__(*args, **kwargs)
        self.fields["selected"].initial = selected_initial

    class Meta:
        model = Unload
        # Nur änderbare Felder für bestehende Wagen
        fields = ['status', 'weight']  # + das Hilfsfeld ist separat definiert
        labels = {
            'status': 'Status',
            'weight': 'Gewicht',
        }

# Formset für neue Zeilen (keine M2M-Felder hier)
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
