from django import forms
from django.forms import modelformset_factory
from warenwirtschaft.models import Shipping, Recycling, Unload


class ShippingHeaderForm(forms.ModelForm):
    class Meta:
        model = Shipping
        #Nur Kopffelder – ohne Recycling-Referenzen
        fields = ["customer", "certificate", "transport", "note"]


class UnloadChoiceForm(forms.Form):
    unload = forms.ModelChoiceField(
        queryset=Unload.objects.filter(status=1),
        label="Vorsortierung wählen"
    )

class RecyclingChoiceForm(forms.Form):
    recycling = forms.ModelChoiceField(
        queryset=Recycling.objects.filter(status=1),
        label="Aufbereitung wählen"
    )

class ShippingForm(forms.ModelForm):
    class Meta:
        model = Shipping
        fields = ["customer", "unload", "certificate", "transport", "note"]

# extra=0, sodass ein leeres Formset gültig ist, wenn der Benutzer nichts hinzugefügt hat
ShippingFormSet = modelformset_factory(
    Shipping,
    form=ShippingForm,
    extra=0,
    can_delete=True,
    validate_min=False,
    validate_max=False,
)

# class ShippingUpdateForm(forms.ModelForm):
#     class Meta:
#         model = Shipping
#         fields = ["box_type", "material", "weight"]
