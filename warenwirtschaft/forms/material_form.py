from django import forms
from warenwirtschaft.models.material import Material


class MaterialForm(forms.ModelForm):
    class Meta:
        model = Material
        fields = ['name', 'delivery', 'unload', 'recycling']