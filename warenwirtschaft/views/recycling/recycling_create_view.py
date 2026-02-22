from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.views import View

from warenwirtschaft.forms.recycling_form import RecyclingForm
from warenwirtschaft.models.recycling import Recycling
from warenwirtschaft.models.unload import Unload
from warenwirtschaft.models_common.choices import StatusChoices
from warenwirtschaft.services.barcode_number_service import BarcodeNumberService


class RecyclingCreateView(View):
    template_name = "recycling/recycling_create.html"
    BARCODE_PREFIX = "Z"

    # --------------------------------------------------
    # Hilfsfunktionen
    # --------------------------------------------------

    def _get_unload(self, unload_pk):
        return get_object_or_404(Unload, pk=unload_pk)

    def _get_all_recyclings(self):
        return Recycling.objects.exclude(status=StatusChoices.ERLEDIGT).order_by("pk")

    def _get_active_ids(self, unload):
        return set(
            Recycling.objects.filter(unloads=unload)
            .values_list("pk", flat=True)
        )

    def _render_page(self, request, unload, new_form):
        return render(
            request,
            self.template_name,
            {
                "selected_menu": "recycling_form",
                "unload": unload,
                "all_recyclings": self._get_all_recyclings(),
                "active_recycling_ids": self._get_active_ids(unload),
                "new_form": new_form,
            },
        )

    # --------------------------------------------------
    # GET
    # --------------------------------------------------

    def get(self, request, unload_pk):
        unload = self._get_unload(unload_pk)
        return self._render_page(request, unload, RecyclingForm())

    # --------------------------------------------------
    # POST
    # --------------------------------------------------

    def post(self, request, unload_pk):
        unload = self._get_unload(unload_pk)

        # IDs aus aktivierten Checkboxen
        selected_ids = request.POST.getlist("recycling_ids")
        selected_ids = set(int(x) for x in selected_ids if x.isdigit())

        current_ids = self._get_active_ids(unload)

        to_add = selected_ids - current_ids
        to_remove = current_ids - selected_ids

        if to_add:
            for r in Recycling.objects.filter(pk__in=to_add):
                r.unloads.add(unload)

        if to_remove:
            for r in Recycling.objects.filter(pk__in=to_remove):
                r.unloads.remove(unload)

       # Optional: neue Fraktion anlegen (ohne extra Checkbox)
        new_form = RecyclingForm(request.POST)

        # Prüfen, ob der Benutzer überhaupt etwas eingegeben hat
        has_new_data = any([
            request.POST.get("material"),
            request.POST.get("box_type"),
            request.POST.get("weight"),
            request.POST.get("note"),
        ])

        if has_new_data:
            if new_form.is_valid():
                new_recycling = new_form.save(commit=False)
                new_recycling.status = StatusChoices.AKTIV_IN_ZERLEGUNG

                BarcodeNumberService.set_barcodes([new_recycling], prefix=self.BARCODE_PREFIX)
                new_recycling.save()
                new_recycling.unloads.add(unload)
            else:
                # Fehler anzeigen
                return self._render_page(request, unload, new_form)

        return redirect(reverse("recycling_create", kwargs={"unload_pk": unload.pk}))