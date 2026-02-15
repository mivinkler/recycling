# warenwirtschaft/views/recycling/recycling_create_view.py

from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.views import View

from warenwirtschaft.forms.recycling_form import RecyclingForm
from warenwirtschaft.models import Unload, Recycling
from warenwirtschaft.services.barcode_number_service import BarcodeNumberService


class RecyclingCreateView(View):
    template_name = "recycling/recycling_create.html"
    BARCODE_PREFIX = "A"

    # --------------------------------------------------
    # Hilfsmethoden
    # --------------------------------------------------

    def _get_unload(self, unload_pk):
        return get_object_or_404(Unload, pk=unload_pk)

    def _get_all_recyclings(self):
        return Recycling.objects.filter(is_active=True)
    
    def _get_active_recyclings(self, unload):
        return Recycling.objects.filter(
            unloads=unload,
            is_active=True,
        ).order_by("pk")

    # --------------------------------------------------
    # GET
    # --------------------------------------------------

    def get(self, request, unload_pk):
        unload = self._get_unload(unload_pk)

        # IDs als Set für schnelle Membership-Checks im Template
        active_recyclings = self._get_active_recyclings(unload)
        active_recycling_ids = set(active_recyclings.values_list("id", flat=True))

        return render(
            request,
            self.template_name,
            {
                "selected_menu": "recycling_form",
                "unload": unload,
                "active_recyclings": active_recyclings,
                "active_recycling_ids": active_recycling_ids,
                "all_recyclings": self._get_all_recyclings(),
                "form": RecyclingForm(),
            },
        )

    # --------------------------------------------------
    # POST
    # --------------------------------------------------

    def post(self, request, unload_pk):
        unload = self._get_unload(unload_pk)

        # Aktive Fraktion verknüpfen
        if "link_recycling" in request.POST:
            recycling_id = request.POST.get("link_recycling")
            recycling = get_object_or_404(Recycling, pk=recycling_id)

            # Beziehung herstellen
            recycling.unloads.add(unload)

            return redirect(
                reverse("recycling_create", kwargs={"unload_pk": unload.pk})
            )

        # Neue Recycling erstellen
        form = RecyclingForm(request.POST)
        if form.is_valid():
            recycling = form.save(commit=False)

            BarcodeNumberService.set_barcodes([unload], prefix=self.BARCODE_PREFIX)

            recycling.save()
            recycling.unloads.add(unload)

            return redirect(reverse("recycling_create", kwargs={"unload_pk": unload.pk}))

        return render(
            request,
            self.template_name,
            {
                "unload": unload,
                "recyclings": self._get_recyclings(unload),
                "form": form,
            },
        )