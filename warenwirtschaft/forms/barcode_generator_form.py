from django import forms
from warenwirtschaft.models.barcode_generator import BarcodeGenerator


class BarcodeGeneratorForm(forms.ModelForm):
    class Meta:
        model = BarcodeGenerator
        fields = [ 'customer', 'box_type', 'material', 'transport', 'weight']