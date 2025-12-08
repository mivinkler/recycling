from django import forms
from django.forms import inlineformset_factory

from warenwirtschaft.models.delivery import Delivery
from warenwirtschaft.models.delivery_unit import DeliveryUnit
from warenwirtschaft.models.customer import Customer


class DeliveryForm(forms.ModelForm):
    customer = forms.ModelChoiceField(
        queryset=Customer.objects.order_by("name"),
        required=True,
        label="Lieferant"
    )

    class Meta:
        model = Delivery
        fields = ["customer", "delivery_receipt"]
        labels = {
            "delivery_receipt": "Lieferschein",
        }

class DeliveryUnitForm(forms.ModelForm):
    class Meta:
        model = DeliveryUnit
        fields = ["box_type", "material", "weight", "note"]


def get_delivery_unit_formset(extra=0):
    """
    Erzeugt ein Inline-Formset für Liefereinheiten.
    :param extra: Anzahl der leeren Formularzeilen
    """
    return inlineformset_factory(
        parent_model=Delivery,
        model=DeliveryUnit,
        form=DeliveryUnitForm,
        fields=DeliveryUnitForm.Meta.fields,
        extra=extra,
        can_delete=True
    )

