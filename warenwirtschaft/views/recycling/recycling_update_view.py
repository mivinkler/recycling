from django.shortcuts import get_object_or_404, render, redirect
from django.views import View

from warenwirtschaft.forms.recycling_form import RecyclingForm
from warenwirtschaft.models.recycling import Recycling
from warenwirtschaft.models.unload import Unload
from warenwirtschaft.models_common.choices import StatusChoices


class RecyclingUpdateView(View):
    template_name = "recycling/recycling_create.html"
    CREATE_FORM_ID = "recycling-create-form"
    UPDATE_FORM_ID = "recycling-update-form"

    # --------------------------------------------------
    # Hilfsfunktionen
    # --------------------------------------------------

    def _unloads_ready(self):
        """Unloads, die auf Zerlegung warten."""
        return Unload.objects.filter(status=StatusChoices.WARTET_AUF_ZERLEGUNG).order_by("pk")

    def _recyclings_active(self):
        """Recyclings, die aktiv in Zerlegung sind."""
        return Recycling.objects.filter(status=StatusChoices.AKTIV_IN_ZERLEGUNG).order_by("pk")

    def _assign_form_id(self, form, form_id):
        if form is None:
            return None

        for field in form.fields.values():
            field.widget.attrs["form"] = form_id

        return form

    def _context(self, *, edit_recycling=None, form=None):
        """Gemeinsamer Template-Kontext (inkl. New-Row-Form)."""
        form = self._assign_form_id(form, self.UPDATE_FORM_ID)
        new_form = self._assign_form_id(RecyclingForm(), self.CREATE_FORM_ID)
        return {
            "selected_menu": "recycling_form",
            "unloads_ready": self._unloads_ready(),
            "recyclings": self._recyclings_active(),
            "status_choices_recycling": StatusChoices.CHOICES,
            "edit_recycling": edit_recycling,
            "form": form,
            "new_form": new_form,  # Neue Zeile bleibt sichtbar
            "create_form_id": self.CREATE_FORM_ID,
            "update_form_id": self.UPDATE_FORM_ID,
        }

    # --------------------------------------------------
    # GET
    # --------------------------------------------------

    def get(self, request, recycling_pk):
        edit_recycling = get_object_or_404(Recycling, pk=recycling_pk)
        form = RecyclingForm(instance=edit_recycling)
        return render(request, self.template_name, self._context(edit_recycling=edit_recycling, form=form))

    # --------------------------------------------------
    # POST
    # --------------------------------------------------

    def post(self, request, recycling_pk):
        edit_recycling = get_object_or_404(Recycling, pk=recycling_pk)
        form = RecyclingForm(request.POST, instance=edit_recycling)

        if form.is_valid():
            recycling = form.save(commit=False)

            # Neues Gewicht (optional) – пустое поле игнорируем
            new_weight = (request.POST.get("new_weight") or "").strip()
            if new_weight:
                recycling.weight = new_weight

            recycling.save()
            return redirect("recycling_create")

        return render(request, self.template_name, self._context(edit_recycling=edit_recycling, form=form))
