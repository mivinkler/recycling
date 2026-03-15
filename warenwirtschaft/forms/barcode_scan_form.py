from django import forms


class BarcodeScanForm(forms.Form):
    scan_barcode = forms.CharField(
        required=False,
        label="Barcode",
        widget=forms.TextInput(
            attrs={
                "placeholder": "Barcode scannen...",
                "autocomplete": "off",
                "autofocus": True,
            }
        ),
    )
