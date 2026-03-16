from django import forms

from warenwirtschaft.models import Material, Recycling
from warenwirtschaft.models_common.choices import BoxTypeChoices, StatusChoices


RECYCLING_FORM_STATUS_CHOICES = [
    (StatusChoices.AKTIV_IN_ZERLEGUNG, "In Zerlegung"),
    (StatusChoices.WARTET_AUF_ABHOLUNG, "Abholbereit"),
]

RECYCLING_FORM_BOX_TYPE_CHOICES = [
    (value, label)
    for value, label in BoxTypeChoices.CHOICES
    if value != BoxTypeChoices.CONTAINER
]


class RecyclingForm(forms.ModelForm):
    def __init__(self, *args, form_id=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["material"].queryset = Material.for_section(
            "recycling",
            include=self.instance.material_id,
        )
        self.fields["status"].choices = RECYCLING_FORM_STATUS_CHOICES
        self.fields["box_type"].choices = RECYCLING_FORM_BOX_TYPE_CHOICES

        if form_id:
            for field in self.fields.values():
                field.widget.attrs["form"] = form_id

    class Meta:
        model = Recycling
        fields = ["material", "box_type", "weight", "status", "note"]
