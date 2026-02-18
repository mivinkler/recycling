# warenwirtschaft/views/recycling/recycling_update_view.py

from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.views import View

from warenwirtschaft.forms.recycling_form import RecyclingForm
from warenwirtschaft.models.recycling import Recycling
from warenwirtschaft.models.unload import Unload
from warenwirtschaft.services.barcode_number_service import BarcodeNumberService


class RecyclingUpdateView(View):
    template_name = "recycling/recycling_update.html"
    BARCODE_PREFIX = "A"

    # --------------------------------------------------
    # Hilfsmethoden
    # --------------------------------------------------

    def _get_unload(self, unload_pk):
        return get_object_or_404(Unload, pk=unload_pk)

    def _get_recycling(self, unload, recycling_pk):
        return get_object_or_404(
            Recycling,
            pk=recycling_pk,
            unloads=unload,
            is_active=True,
        )

    def _redirect_create(self, unload):
        return redirect(reverse("recycling_create", kwargs={"unload_pk": unload.pk}))

    def _redirect_update(self, unload, recycling_pk):
        return redirect(
            reverse(
                "recycling_update",
                kwargs={"unload_pk": unload.pk, "recycling_pk": recycling_pk},
            )
        )

    def _build_context(self, unload, edit_recycling, form):
        active_recyclings = Recycling.objects.filter(unloads=unload, is_active=True).order_by("pk")
        active_recycling_ids = set(active_recyclings.values_list("id", flat=True))

        return {
            "selected_menu": "recycling_form",
            "unload": unload,
            "active_recyclings": active_recyclings,
            "active_recycling_ids": active_recycling_ids,
            "all_recyclings": Recycling.objects.filter(is_active=True).order_by("pk"),
            "edit_recycling": edit_recycling,
            "form": form,
        }

    # --------------------------------------------------
    # GET
    # --------------------------------------------------

    def get(self, request, unload_pk, recycling_pk):
        unload = self._get_unload(unload_pk)
        edit_recycling = self._get_recycling(unload, recycling_pk)

        return render(
            request,
            self.template_name,
            self._build_context(unload, edit_recycling, RecyclingForm(instance=edit_recycling)),
        )

    # --------------------------------------------------
    # POST
    # --------------------------------------------------

    def post(self, request, unload_pk, recycling_pk):
        unload = self._get_unload(unload_pk)

        # Mini-Form pro Button -> recycling_id kommt als hidden input
        if request.POST.get("recycling_id"):
            recycling_id = request.POST.get("recycling_id")
            recycling = get_object_or_404(Recycling, pk=recycling_id, is_active=True)

            recycling.unloads.add(unload)
            return self._redirect_update(unload, recycling_id)

        edit_recycling = self._get_recycling(unload, recycling_pk)
        form = RecyclingForm(request.POST, instance=edit_recycling)

        if form.is_valid():
            recycling = form.save(commit=False)

            BarcodeNumberService.set_barcodes([unload], prefix=self.BARCODE_PREFIX)

            recycling.save()

            # Checkbox: wenn nicht gesetzt -> unlink und zurück
            is_checked = request.POST.get("selected_recycling") == str(recycling.pk)
            if not is_checked:
                recycling.unloads.remove(unload)
                return self._redirect_create(unload)

            return self._redirect_update(unload, recycling.pk)

        return render(
            request,
            self.template_name,
            self._build_context(unload, edit_recycling, form),
        )