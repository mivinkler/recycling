from django import forms
from warenwirtschaft.models.barcode_generator import BarcodeGenerator


class BarcodeGeneratorForm(forms.ModelForm):
    class Meta:
        model = BarcodeGenerator
        fields = ['area', 'customer', 'customer', 'box_type', 'material', 'weight']