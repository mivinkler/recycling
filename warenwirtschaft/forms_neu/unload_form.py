from django import forms
from django.forms import inlineformset_factory
from warenwirtschaft.models.unload import Unload
from warenwirtschaft.models.delivery_unit import DeliveryUnit


# Auswahl einer Liefereinheit (nicht ModelForm!)
class DeliveryUnitForm(forms.Form):
    delivery_unit = forms.ModelChoiceField(
        queryset=DeliveryUnit.objects.filter(status=1),
        label="Liefereinheit"
    )

# Formular für einen einzelnen Unload
class UnloadForm(forms.ModelForm):
    class Meta:
        model = Unload
        fields = ['box_type', 'material', 'weight', 'target', 'note']

# Dynamisch erzeugter InlineFormSet für Unload
def get_unload_formset(extra=0):
    return inlineformset_factory(
        parent_model=DeliveryUnit,
        model=Unload,
        form=UnloadForm,
        fields=UnloadForm.Meta.fields,  # Meta aus UnloadForm
        extra=extra, # Leere Felder. UnloadCreateView hat extra=1 und UnloadUpdateView hat extra=0, s.a. view "formset_class"
        can_delete=True
    )
