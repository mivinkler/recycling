from django.shortcuts import get_object_or_404, render, redirect
from django.views import View
from django.utils import timezone

from warenwirtschaft.forms.recycling_form import RecyclingForm
from warenwirtschaft.models.unload import Unload
from warenwirtschaft.models.recycling import Recycling
from warenwirtschaft.models_common.choices import StatusChoices
from warenwirtschaft.services.barcode_number_service import BarcodeNumberService


class RecyclingCreateView(View):
    template_name = "recycling/recycling_create.html"
    BARCODE_PREFIX = "Z"

    # --------------------------------------------------
    # Hilfsfunktionen
    # --------------------------------------------------

    def _unloads_ready(self):
        """Unloads, die auf Zerlegung warten."""
        return Unload.objects.filter(
            status=StatusChoices.WARTET_AUF_ZERLEGUNG
        ).order_by("pk")

    def _unloads_done_today(self):
        """Unloads, die heute abgeschlossen wurden (inactive_at = heute)."""
        today = timezone.localdate()
        return Unload.objects.filter(
            status=StatusChoices.ERLEDIGT,
            inactive_at__date=today,
        ).order_by("-inactive_at", "-pk")

    def _recyclings_active(self):
        """Recyclings, die aktiv in Zerlegung sind."""
        return Recycling.objects.filter(
            status=StatusChoices.AKTIV_IN_ZERLEGUNG
        ).order_by("pk")

    def _context(self, *, new_form=None, edit_recycling=None, form=None):
        """Gemeinsamer Template-Kontext."""
        return {
            "selected_menu": "recycling_form",
            "unloads_ready": self._unloads_ready(),
            "unloads_done_today": self._unloads_done_today(),
            "recyclings": self._recyclings_active(),
            "status_choices_recycling": StatusChoices.CHOICES,
            "new_form": new_form or RecyclingForm(),
            "edit_recycling": edit_recycling,
            "form": form,
        }

    # --------------------------------------------------
    # GET
    # --------------------------------------------------

    def get(self, request):
        return render(request, self.template_name, self._context())

    # --------------------------------------------------
    # POST
    # --------------------------------------------------

    def post(self, request):
        # 0) "Zurücksetzen" (Unload zurück nach "Wartet auf Zerlegung")
        if "reset_unload" in request.POST:
            unload_id = request.POST.get("unload_id")
            if unload_id and unload_id.isdigit():
                unload = get_object_or_404(
                    Unload,
                    pk=int(unload_id),
                    status=StatusChoices.ERLEDIGT,
                )

                # Wagen zurücksetzen: Status und inactive_at zurücksetzen
                unload.status = StatusChoices.WARTET_AUF_ZERLEGUNG
                unload.inactive_at = None
                unload.save(update_fields=["status", "inactive_at"])

            return redirect("recycling_create")

        # 1) "Zufügen" (unload_id vorhanden)
        unload_id = request.POST.get("unload_id")
        if unload_id and unload_id.isdigit():
            unload = get_object_or_404(
                Unload,
                pk=int(unload_id),
                status=StatusChoices.WARTET_AUF_ZERLEGUNG,
            )

            # Alle aktiven Recyclings mit Unload verknüpfen
            for r in self._recyclings_active():
                r.unloads.add(unload)

            # Unload abschließen
            unload.status = StatusChoices.ERLEDIGT
            unload.inactive_at = timezone.now()
            unload.save(update_fields=["status", "inactive_at"])

            return redirect("recycling_create")

        # 2) Neue Recycling-Zeile anlegen
        new_form = RecyclingForm(request.POST)
        if new_form.is_valid():
            new_recycling = new_form.save(commit=False)

            BarcodeNumberService.set_barcodes([new_recycling], prefix=self.BARCODE_PREFIX)

            new_recycling.status = StatusChoices.AKTIV_IN_ZERLEGUNG
            new_recycling.save()
            return redirect("recycling_create")

        # Fehler anzeigen
        return render(request, self.template_name, self._context(new_form=new_form))