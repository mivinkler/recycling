from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
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

    def _get_unloads_ready(self):
        return Unload.objects.filter(
            status=StatusChoices.WARTET_AUF_ZERLEGUNG
            ).order_by("pk")

    def _get_recyclings_active(self):
        return Recycling.objects.filter(
            status=StatusChoices.AKTIV_IN_ZERLEGUNG
            ).order_by("pk")


    # --------------------------------------------------
    # GET
    # --------------------------------------------------

    def get(self, request):
        return render(
            request, 
            self.template_name, 
            {
                "selected_menu": "recycling_form",
                "unloads_ready": self._get_unloads_ready(),
                "recyclings": self._get_recyclings_active(),
                "status_choices_recycling": StatusChoices.CHOICES,
                "new_form": RecyclingForm(),
            },
        )

    # --------------------------------------------------
    # POST
    # --------------------------------------------------

    def post(self, request):
        # 1) Wenn unload_id angekommen ist -> "Zufügen"
        unload_id = request.POST.get("unload_id")
        if unload_id:
            unload = get_object_or_404(
                Unload,
                pk=int(unload_id),
                status=StatusChoices.WARTET_AUF_ZERLEGUNG,
            )

            recyclings = self._get_recyclings_active()
            for recycling in recyclings:
                recycling.unloads.add(unload)

            unload.status = StatusChoices.ERLEDIGT
            unload.save(update_fields=["status"])

            return redirect(reverse("recycling_create"))

        # 2) Ansonsten -> „Neue Recycling-Zeile“ erstellen
        new_form = RecyclingForm(request.POST)
        if new_form.is_valid():
            new_recycling = new_form.save(commit=False)
            new_recycling.status = StatusChoices.AKTIV_IN_ZERLEGUNG
            new_recycling.save()
            return redirect(reverse("recycling_create"))

        # Im Fehlerfall die Fehlerseite anzeigen.
        return render(
            request,
            self.template_name,
            {
                "selected_menu": "recycling_form",
                "unloads_ready": self._get_unloads_ready(),
                "recyclings": self._get_recyclings_active(),
                "status_choices_recycling": StatusChoices.CHOICES,
                "new_form": new_form,
            },
        )