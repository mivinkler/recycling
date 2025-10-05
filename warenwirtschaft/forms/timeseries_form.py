# Formulare für den Time-Series-Report (Filterleiste)
from django import forms
from warenwirtschaft.models.customer import Customer
from warenwirtschaft.models.material import Material

# ISO-Widget für HTML5 <input type="date">
class ISODateInput(forms.DateInput):
    input_type = "date"
    def __init__(self, **kwargs):
        # HTML erwartet YYYY-MM-DD
        kwargs.setdefault("format", "%Y-%m-%d")
        super().__init__(**kwargs)

class TimeSeriesFilterForm(forms.Form):
    customer = forms.ModelChoiceField(
        queryset=Customer.objects.all(),
        required=False,
        label="Lieferant"
    )
    material = forms.ModelChoiceField(
        queryset=Material.objects.all(),
        required=False,
        label="Material"
    )

    # Wichtig: gleicher Formatstring für Widget + Parser
    date_from = forms.DateField(
        required=True,
        label="Von",
        widget=ISODateInput(),
        input_formats=["%Y-%m-%d"],
        localize=False,  # keine Lokalisierung im Feld
    )
    date_to = forms.DateField(
        required=True,
        label="Bis",
        widget=ISODateInput(),
        input_formats=["%Y-%m-%d"],
        localize=False,
    )
