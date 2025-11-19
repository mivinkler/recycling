# warenwirtschaft/forms/unload_form.py
from django import forms
from django.forms import modelformset_factory
from warenwirtschaft.models import Unload, DeliveryUnit

class DeliveryUnitSelectForm(forms.Form):
    #Initial kein QuerySet – wir setzen es zur Laufzeit im View
    delivery_unit = forms.ModelChoiceField(
        queryset=DeliveryUnit.objects.none(),
        label="Liefereinheit",
        widget=forms.Select(attrs={"id": "id_delivery_unit"})
    )

    def __init__(self, *args, queryset=None, **kwargs):
        super().__init__(*args, **kwargs)

        #Fallback: nur „aktive“ Einheiten und nur benötigte Felder
        if queryset is None:
            queryset = (DeliveryUnit.objects
                        .filter(status=1)                       # nur relevante Einheiten für Vorsortierung
                        .only("id", "status", "box_type", "weight", "note", "barcode")
                        .order_by("pk")[:500])                   # Sicherheits-Deckel; не пагинация, просто ограничитель

        self.fields["delivery_unit"].queryset = queryset

        #Schlanke Label-Funktion (kein Zugriff auf teure Relationen!)
        self.fields["delivery_unit"].label_from_instance = lambda du: (
            f"{du.barcode or f'L{du.id}'} • {du.get_box_type_display()} • {du.weight or 0} kg"
        )


class UnloadForm(forms.ModelForm):
    class Meta:
        model = Unload
        fields = ['box_type', 'material', 'weight', 'status', 'note']
        labels = {
            'box_type': 'Behälter', 
            'material': 'Material',
            'weight': 'Gewicht', 
            'status': 'Status', 
            'note': 'Anmerkung'
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
        fields = ['status', 'weight', 'note']  # + das Hilfsfeld ist separat definiert
        labels = {
            'status': 'Status',
            'weight': 'Gewicht',
            'note': 'Anmerkung'
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
