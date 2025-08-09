from django import forms
from django.forms import modelformset_factory
from warenwirtschaft.models import Recycling, Unload

class UnloadChoiceForm(forms.Form):
    unload = forms.ModelChoiceField(
        queryset=Unload.objects.filter(status=1, target=2),
        label="Vorsortierung wählen"
    )

class RecyclingForm(forms.ModelForm):
    class Meta:
        model = Recycling
        # ✨ «unloads» убираем из формы — это M2M, ты его выставляешь в view
        fields = ["box_type", "material", "weight"]

# ✨ extra=0, чтобы пустой formset был валиден, если пользователь ничего не добавлял
RecyclingFormSet = modelformset_factory(
    Recycling,
    form=RecyclingForm,
    extra=0,
    can_delete=True,
    validate_min=False,
    validate_max=False,
)

class RecyclingUpdateForm(forms.ModelForm):
    class Meta:
        model = Recycling
        fields = ["box_type", "material", "weight"]
