from django.shortcuts import get_object_or_404, render, redirect
from django.views import View

from warenwirtschaft.forms.recycling_form import RecyclingForm
from warenwirtschaft.models.unload import Unload
from warenwirtschaft.models.recycling import Recycling
from warenwirtschaft.models_common.choices import StatusChoices


class RecyclingCreateView(View):
    template_name = "recycling/recycling_create.html"

    # --------------------------------------------------
    # Hilfsfunktionen
    # --------------------------------------------------

    def _unloads_ready(self):
        """Unloads, die auf Zerlegung warten."""
        return Unload.objects.filter(status=StatusChoices.WARTET_AUF_ZERLEGUNG).order_by("pk")

    def _recyclings_active(self):
        """Recyclings, die aktiv in Zerlegung sind."""
        return Recycling.objects.filter(status=StatusChoices.AKTIV_IN_ZERLEGUNG).order_by("pk")

    def _context(self, *, new_form=None, edit_recycling=None, form=None):
        """Gemeinsamer Template-Kontext."""
        return {
            "selected_menu": "recycling_form",
            "unloads_ready": self._unloads_ready(),
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
            unload.save(update_fields=["status"])

            return redirect("recycling_create")

        # 2) Neue Recycling-Zeile anlegen
        new_form = RecyclingForm(request.POST)
        if new_form.is_valid():
            new_recycling = new_form.save(commit=False)
            new_recycling.status = StatusChoices.AKTIV_IN_ZERLEGUNG
            new_recycling.save()
            return redirect("recycling_create")

        # Fehler anzeigen
        return render(request, self.template_name, self._context(new_form=new_form))