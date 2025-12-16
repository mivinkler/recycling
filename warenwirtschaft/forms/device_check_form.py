from __future__ import annotations

from django import forms
from django.forms import modelformset_factory
from warenwirtschaft.models.device_check import DeviceCheck


class DeviceCheckForm(forms.ModelForm):
    class Meta:
        model = DeviceCheck
        fields = ["box_type", "material", "purpose", "weight", "note"]
        labels = {
            "box_type": "Behälter",
            "weight": "Gewicht",
            "material": "Material",
            "purpose": "Zweck",
            "note": "Anmerkung",
        }


def get_device_check_formset(extra=0):
    return modelformset_factory(
        DeviceCheck,
        form=DeviceCheckForm,
        extra=extra,
        can_delete=True,
    )
