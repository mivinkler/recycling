from django import forms
from django.forms import modelformset_factory, inlineformset_factory
from warenwirtschaft.models import Unload, DeliveryUnit, Delivery



class DeliveryUnitChoiceForm(forms.Form):
    # DE: Auswahl EINER Liefereinheit, zu der Unloads zugeordnet/erstellt werden
    delivery_unit = forms.ModelChoiceField(
        queryset=DeliveryUnit.objects.filter(status=1),
        label="Liefereinheit"
    )

class UnloadForm(forms.ModelForm):
    class Meta:
        model = Unload
        fields = ['box_type', 'material', 'weight', 'note']

def get_unload_formset(extra=0):
    # DE: Wie bei deinem Recycling-Beispiel – ohne FK-Zwang
    return modelformset_factory(
        Unload,
        form=UnloadForm,
        extra=extra,      # z.B. Create: 1, Update: 0
        can_delete=True,
        validate_min=False,
        validate_max=False,
    )