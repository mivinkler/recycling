from django.views import View
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse

from warenwirtschaft.forms.unload_form import ExistingEditFormSet, DeliveryUnitSelectForm
from warenwirtschaft.models import DeliveryUnit
from warenwirtschaft.models import Unload

class UnloadSelectView(View):
    template_name = "unload/unload_select.html"

    def get(self, request):
        form = DeliveryUnitSelectForm(request.GET or None)
        if "delivery_unit" in request.GET and form.is_valid():
            return self._redirect_by_status(form.cleaned_data["delivery_unit"])
        
        vorhandene_unloads = Unload.objects.filter(status__in=[0, 1]).order_by("pk")
        context = {
            "form": form,
            "vorhandene_unloads": vorhandene_unloads,
        }

        return render(request, self.template_name, context)

    def post(self, request):
        form = DeliveryUnitSelectForm(request.POST)
        if form.is_valid():
            return self._redirect_by_status(form.cleaned_data["delivery_unit"])
        return render(request, self.template_name, {"form": form})

    def _redirect_by_status(self, du: DeliveryUnit):
        if du.status == 1:
            return redirect(reverse("unload_update", kwargs={"delivery_unit_pk": du.pk}))
        return redirect(reverse("unload_create", kwargs={"delivery_unit_pk": du.pk}))
