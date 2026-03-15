from django.utils import timezone

from warenwirtschaft.models import Recycling, Unload
from warenwirtschaft.models_common.choices import BoxTypeChoices, StatusChoices


RECYCLING_FORM_STATUS_CHOICES = [
    (StatusChoices.AKTIV_IN_ZERLEGUNG, "In Zerlegung"),
    (StatusChoices.WARTET_AUF_ABHOLUNG, "Abholbereit"),
]

RECYCLING_LIST_STATUS_CHOICES = [
    *RECYCLING_FORM_STATUS_CHOICES,
    (StatusChoices.ERLEDIGT, "Erledigt"),
]

RECYCLING_FORM_BOX_TYPE_CHOICES = [
    (value, label)
    for value, label in BoxTypeChoices.CHOICES
    if value != BoxTypeChoices.CONTAINER
]

RECYCLING_LIST_BOX_TYPE_CHOICES = list(RECYCLING_FORM_BOX_TYPE_CHOICES)

RECYCLING_VISIBLE_STATUSES = (
    StatusChoices.AKTIV_IN_ZERLEGUNG,
    StatusChoices.WARTET_AUF_ABHOLUNG,
)


class RecyclingPageMixin:
    template_name = "recycling/recycling_create.html"
    CREATE_FORM_ID = "recycling-create-form"
    UPDATE_FORM_ID = "recycling-update-form"

    def _get_recyclings_visible(self):
        return Recycling.objects.filter(status__in=RECYCLING_VISIBLE_STATUSES).order_by("pk")

    def _get_recyclings_in_progress(self):
        return Recycling.objects.filter(status=StatusChoices.AKTIV_IN_ZERLEGUNG).order_by("pk")

    def _get_unloads_ready_for_recycling(self):
        return Unload.objects.filter(status=StatusChoices.WARTET_AUF_ZERLEGUNG).order_by("pk")

    def _get_unloads_finished_today(self):
        today = timezone.localdate()
        return Unload.objects.filter(
            status=StatusChoices.ERLEDIGT,
            inactive_at__date=today,
        ).order_by("-inactive_at", "-pk")

    def _bind_form_to_form_id(self, form, form_id):
        if form is None:
            return None

        for field in form.fields.values():
            field.widget.attrs["form"] = form_id

        return form

    def _build_context(self, *, new_form=None, edit_recycling=None, form=None, scan_form=None):
        # Lazy imports vermeiden zyklische Abhaengigkeiten mit den Formularen.
        from warenwirtschaft.forms.barcode_scan_form import BarcodeScanForm
        from warenwirtschaft.forms.recycling_form import RecyclingForm

        return {
            "selected_menu": "recycling_form",
            "unloads_ready": self._get_unloads_ready_for_recycling(),
            "unloads_done_today": self._get_unloads_finished_today(),
            "recyclings": self._get_recyclings_visible(),
            "new_form": self._bind_form_to_form_id(new_form or RecyclingForm(), self.CREATE_FORM_ID),
            "edit_recycling": edit_recycling,
            "form": self._bind_form_to_form_id(form, self.UPDATE_FORM_ID),
            "scan_form": scan_form or BarcodeScanForm(),
            "create_form_id": self.CREATE_FORM_ID,
            "update_form_id": self.UPDATE_FORM_ID,
        }
