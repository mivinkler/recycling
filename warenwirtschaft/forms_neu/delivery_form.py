from django import forms
from django.forms import inlineformset_factory
from warenwirtschaft.models.delivery import Delivery
from warenwirtschaft.models.delivery_unit import DeliveryUnit


class DeliveryForm(forms.ModelForm):
    class Meta:
        model = Delivery
        fields = ['supplier', 'delivery_receipt', 'note']
        widgets = {
            'note': forms.Textarea(attrs={'rows': 3}),
        }

# Formular für einzelne Liefereinheit
class DeliveryUnitForm(forms.ModelForm):
    class Meta:
        model = DeliveryUnit
        fields = ['box_type', 'material', 'weight', 'note']

# Fabrik für Formset
# Funktion zum Erzeugen des Formsets mit dynamischem 'extra'
def get_delivery_unit_formset(extra=0):
    return inlineformset_factory(
        parent_model=Delivery,
        model=DeliveryUnit,
        form=DeliveryUnitForm,
        fields=DeliveryUnitForm.Meta.fields,
        extra=extra,
        can_delete=True
    )
