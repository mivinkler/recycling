from django.views import View
from django.shortcuts import render, redirect
from django.urls import reverse

from django.db.models import Q
from warenwirtschaft.forms.unload_form import DeliveryUnitSelectForm
from warenwirtschaft.models import DeliveryUnit, Unload


class UnloadSelectView(View):
    template_name = "unload/unload_select.html"

    def get(self, request):
        # Auswahl: nur aktive Liefereinheiten für die Vorsortierung
        du_qs = (
            DeliveryUnit.objects
            .filter(status=1)
            .only("id", "status", "box_type", "weight", "barcode")
            .order_by("pk")
        )

        form = DeliveryUnitSelectForm(request.GET or None, queryset=du_qs)

        # Wenn eine DeliveryUnit gewählt wurde, direkt weiterleiten (create|update)
        if "delivery_unit" in request.GET and form.is_valid():
            return self._redirect_by_relation(form.cleaned_data["delivery_unit"])

        # Übersicht aktiver Wagen
        vorhandene_unloads = (
            Unload.objects
            .filter(status__in=[0, 1])
            .select_related("material")             # verhindert N+1 bei {{ u.material }}
            .only("id", "status", "box_type", "weight", "created_at", "material__name")
            .order_by("pk")
        )

        context = {
            "form": form,
            "vorhandene_unloads": vorhandene_unloads,
            "selected_menu": "unload_form",
        }
        return render(request, self.template_name, context)

    def post(self, request):
        du_qs = (
            DeliveryUnit.objects
            .filter(status=1)
            .only("id", "status", "box_type", "weight", "barcode")
            .order_by("pk")
        )
        form = DeliveryUnitSelectForm(request.POST, queryset=du_qs)
        if form.is_valid():
            return self._redirect_by_relation(form.cleaned_data["delivery_unit"])
        return render(request, self.template_name, {"form": form, "selected_menu": "unload_select"})

    # ===== Intern =====

    def _redirect_by_relation(self, du: DeliveryUnit):
        """
        Regel:
        - Gibt es mind. einen Unload (status=1), der mit dieser Liefereinheit verknüpft ist? → update
        - Sonst → create
        """
        has_active_unload = Unload.objects.filter(status=1, delivery_units=du).exists()
        if has_active_unload:
            return redirect(reverse("unload_update", kwargs={"delivery_unit_pk": du.pk}))
        return redirect(reverse("unload_create", kwargs={"delivery_unit_pk": du.pk}))
