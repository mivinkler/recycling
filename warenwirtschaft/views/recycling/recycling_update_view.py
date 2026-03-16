from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views import View

from warenwirtschaft.forms.barcode_scan_form import BarcodeScanForm
from warenwirtschaft.forms.recycling_form import RecyclingForm
from warenwirtschaft.models import Recycling, Unload
from warenwirtschaft.models_common.choices import StatusChoices


class RecyclingUpdateView(View):
    template_name = "recycling/recycling_create.html"
    CREATE_FORM_ID = "recycling-create-form"
    UPDATE_FORM_ID = "recycling-update-form"
    VISIBLE_STATUSES = (
        StatusChoices.AKTIV_IN_ZERLEGUNG,
        StatusChoices.WARTET_AUF_ABHOLUNG,
    )

    def _get_recycling(self, recycling_pk):
        return get_object_or_404(Recycling, pk=recycling_pk)

    def _get_recyclings(self):
        return (
            Recycling.objects.filter(status__in=self.VISIBLE_STATUSES)
            .select_related("material")
            .order_by("pk")
        )

    def _get_unloads_ready(self):
        return (
            Unload.objects.filter(status=StatusChoices.WARTET_AUF_ZERLEGUNG)
            .select_related("material")
            .order_by("pk")
        )

    def _get_unloads_finished_today(self):
        today = timezone.localdate()
        return (
            Unload.objects.filter(
                status=StatusChoices.ERLEDIGT,
                inactive_at__date=today,
            )
            .select_related("material")
            .order_by("-inactive_at", "-pk")
        )

    def _get_context(self, *, recycling, form):
        return {
            "selected_menu": "recycling_form",
            "unloads_ready": self._get_unloads_ready(),
            "unloads_done_today": self._get_unloads_finished_today(),
            "recyclings": self._get_recyclings(),
            "new_form": RecyclingForm(form_id=self.CREATE_FORM_ID),
            "edit_recycling": recycling,
            "form": form,
            "scan_form": BarcodeScanForm(),
            "create_form_id": self.CREATE_FORM_ID,
            "update_form_id": self.UPDATE_FORM_ID,
        }

    def _render_page(self, request, *, recycling, form):
        return render(
            request,
            self.template_name,
            self._get_context(recycling=recycling, form=form),
        )

    def _apply_new_weight(self, recycling, raw_weight):
        new_weight = (raw_weight or "").strip()
        if new_weight:
            # Leeres Feld soll das vorhandene Gewicht nicht ueberschreiben.
            recycling.weight = new_weight

    def get(self, request, recycling_pk):
        recycling = self._get_recycling(recycling_pk)
        form = RecyclingForm(instance=recycling, form_id=self.UPDATE_FORM_ID)
        return self._render_page(request, recycling=recycling, form=form)

    def post(self, request, recycling_pk):
        recycling = self._get_recycling(recycling_pk)
        form = RecyclingForm(
            request.POST,
            instance=recycling,
            form_id=self.UPDATE_FORM_ID,
        )

        if form.is_valid():
            recycling = form.save(commit=False)
            self._apply_new_weight(recycling, request.POST.get("new_weight"))
            recycling.save()
            return redirect("recycling_create")

        return self._render_page(request, recycling=recycling, form=form)
