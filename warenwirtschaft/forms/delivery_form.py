from django import forms
from django.forms import inlineformset_factory
from warenwirtschaft.models.delivery import Delivery
from warenwirtschaft.models.delivery_unit import DeliveryUnit
from warenwirtschaft.models.customer import Customer


class DeliveryForm(forms.ModelForm):
    class Meta:
        model = Delivery
        fields = ['customer', 'delivery_receipt', 'note']
        widgets = {
            'note': forms.Textarea(attrs={'rows': 3}),
        }

    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['customer'].queryset = Customer.objects.all().order_by('name')
        self.fields['customer'].empty_label = '---------'
        self.fields['customer'].required = True 

    def clean(self):
        cleaned = super().clean()
        if not cleaned.get('customer'):
            self.add_error('customer', 'Bitte wählen Sie einen Lieferanten.')
        return cleaned

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
