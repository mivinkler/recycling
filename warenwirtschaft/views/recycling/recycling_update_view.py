# warenwirtschaft/views/recycling/recycling_update_view.py

from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.views import View

from warenwirtschaft.forms.recycling_form import RecyclingForm
from warenwirtschaft.models.recycling import Recycling
from warenwirtschaft.models.unload import Unload
from warenwirtschaft.models_common.choices import StatusChoices


class RecyclingUpdateView(View):
    template_name = "recycling/recycling_create.html"  # тот же шаблон, что и список

    # --------------------------------------------------
    # Hilfsfunktionen
    # --------------------------------------------------

    def _get_recycling(self, recycling_pk):
        """Recycling laden (404, falls nicht vorhanden)."""
        return get_object_or_404(Recycling, pk=recycling_pk)

    def _get_unloads_ready(self):
        """Unloads im Status WARTET_AUF_ZERLEGUNG anzeigen."""
        return Unload.objects.filter(status=StatusChoices.WARTET_AUF_ZERLEGUNG).order_by("pk")

    def _get_recyclings_active(self):
        """Recyclings im Status AKTIV_IN_ZERLEGUNG anzeigen."""
        return Recycling.objects.filter(status=StatusChoices.AKTIV_IN_ZERLEGUNG).order_by("pk")

    def _build_context(self, edit_recycling=None, form=None):
        return {
            "selected_menu": "recycling_form",
            "unloads_ready": self._get_unloads_ready(),
            "recyclings": self._get_recyclings_active(),
            "edit_recycling": edit_recycling,
            "form": form,
            "status_choices_recycling": StatusChoices.CHOICES,
        }

    # --------------------------------------------------
    # GET
    # --------------------------------------------------

    def get(self, request, recycling_pk):
        edit_recycling = self._get_recycling(recycling_pk)
        form = RecyclingForm(instance=edit_recycling)

        return render(request, self.template_name, self._build_context(edit_recycling, form))

    # --------------------------------------------------
    # POST
    # --------------------------------------------------

    def post(self, request, recycling_pk):
        edit_recycling = self._get_recycling(recycling_pk)
        form = RecyclingForm(request.POST, instance=edit_recycling)

        if form.is_valid():
            form.save()
            return redirect(reverse("recycling_create"))

        return render(request, self.template_name, self._build_context(edit_recycling, form))