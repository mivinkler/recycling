from django import forms

from warenwirtschaft.models import Material, Recycling
from warenwirtschaft.recycling_page_mixin import (
    RECYCLING_FORM_BOX_TYPE_CHOICES,
    RECYCLING_FORM_STATUS_CHOICES,
)


class RecyclingForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["material"].queryset = Material.for_section(
            "recycling",
            include=self.instance.material_id,
        )
        self.fields["status"].choices = RECYCLING_FORM_STATUS_CHOICES
        self.fields["box_type"].choices = RECYCLING_FORM_BOX_TYPE_CHOICES

    class Meta:
        model = Recycling
        fields = ["material", "box_type", "weight", "status", "note"]
