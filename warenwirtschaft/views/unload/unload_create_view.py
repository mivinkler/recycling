# warenwirtschaft/views/unload/unload_manage_view.py
from __future__ import annotations

from django.contrib import messages
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views import View

from warenwirtschaft.forms.unload_form import ExistingEditFormSet, UnloadFormSet
from warenwirtschaft.models import DeliveryUnit, Unload
from warenwirtschaft.models_common.choices import StatusChoices
from warenwirtschaft.services.barcode_number_service import BarcodeNumberService


class UnloadCreateView(View):
    """
    Ein gemeinsamer Screen für Create + Update der Vorsortierung zu einer Liefereinheit.

    Idee:
    - Es gibt immer zwei Bereiche:
      (1) bestehende offene Unloads (jeweils Einzel-Form mit Checkbox 'selected')
      (2) neue Unloads als Formset
    - Der Unterschied Create/Update ist nur das Template (und dass beim Update
      bereits verknüpfte Unloads als 'selected' vorausgewählt sind).
    """

    # --- Konfiguration ---
    mode: str = "update"  # wird über as_view(mode="create"/"update") gesetzt

    template_name_create = "unload/unload_create.html"
    template_name_update = "unload/unload_update.html"

    OPEN_STATUS = StatusChoices.IN_VORSORTIERUNG
    BARCODE_PREFIX = "S"
    NEW_PREFIX = "new"

    # ----------------------------------------------------------
    # GET
    # ----------------------------------------------------------
    def get(self, request, delivery_unit_pk: int):
        delivery_unit = self._get_delivery_unit(delivery_unit_pk)

        new_formset = self._get_new_formset()
        vorhandene_forms = self._build_existing_forms(delivery_unit)

        context = self._get_context_data(
            delivery_unit=delivery_unit,
            formset=new_formset,
            vorhandene_forms=vorhandene_forms,
        )
        return self._render(request, context)

    # ----------------------------------------------------------
    # POST
    # ----------------------------------------------------------
    def post(self, request, delivery_unit_pk: int):
        delivery_unit = self._get_delivery_unit(delivery_unit_pk)

        new_formset = self._get_new_formset(data=request.POST)
        vorhandene_forms = self._build_existing_forms(delivery_unit, data=request.POST)

        valid_new = new_formset.is_valid()
        valid_existing = all(f.is_valid() for f, _ in vorhandene_forms)

        if not (valid_new and valid_existing):
            messages.error(request, "⚠️ Bitte Eingaben prüfen.")
            context = self._get_context_data(
                delivery_unit=delivery_unit,
                formset=new_formset,
                vorhandene_forms=vorhandene_forms,
            )
            return self._render(request, context)

        # IDs der ausgewählten bestehenden Unloads (Checkboxen in Einzel-Forms)
        selected_ids = {
            str(f.instance.pk)
            for f, _ in vorhandene_forms
            if f.cleaned_data.get("selected")
        }

        # Nur geänderte bestehende speichern
        changed_existing = [f for f, _ in vorhandene_forms if f.has_changed()]

        with transaction.atomic():
            # 1) bestehende Unloads speichern (status/weight/note)
            for f in changed_existing:
                f.save()

            # 2) M2M-Verknüpfung gemäß Auswahl synchronisieren
            #    (für Create ist das ebenfalls ok – es gab vorher keine Auswahl)
            open_qs = self._get_open_unloads_qs()
            for obj in open_qs:
                if str(obj.pk) in selected_ids:
                    obj.delivery_units.add(delivery_unit)
                else:
                    obj.delivery_units.remove(delivery_unit)

            # 3) neue Unloads speichern + verknüpfen (inkl. Barcode)
            self._save_new_formset(new_formset, delivery_unit)

        messages.success(request, "✅ Die Daten sind gespeichert.")
        return redirect(self._get_success_url(delivery_unit.pk))

    # ----------------------------------------------------------
    # Helpers
    # ----------------------------------------------------------
    def _template_name(self) -> str:
        """Wählt je nach Modus das Template aus."""
        return self.template_name_create if self.mode == "create" else self.template_name_update

    def _get_delivery_unit(self, pk: int) -> DeliveryUnit:
        """Liefert die zugehörige Liefereinheit oder 404."""
        return get_object_or_404(DeliveryUnit, pk=pk)

    def _get_open_unloads_qs(self):
        """Basis-Query für alle offenen, aktiven Unloads."""
        return (
            Unload.objects
            .filter(is_active=True, status=self.OPEN_STATUS)
            .order_by("pk")
        )

    def _get_new_formset(self, data=None):
        """Formset für neue Unloads."""
        kwargs = {"queryset": Unload.objects.none(), "prefix": self.NEW_PREFIX}
        if data is not None:
            kwargs["data"] = data
        return UnloadFormSet(**kwargs)

    def _build_existing_forms(self, delivery_unit: DeliveryUnit, data=None):
        """
        Erstellt Einzel-Forms für alle offenen, aktiven Unloads.

        - GET: selected_initial kommt aus der M2M-Beziehung
        - POST: data überschreibt initial automatisch
        """
        ExistingEditForm = ExistingEditFormSet.form

        selected_ids_db = set(
            Unload.objects
            .filter(delivery_units=delivery_unit, is_active=True)
            .values_list("pk", flat=True)
        )

        forms = []
        for obj in self._get_open_unloads_qs():
            form = ExistingEditForm(
                data=data if data is not None else None,
                instance=obj,
                prefix=f"exist_{obj.pk}",
                selected_initial=(obj.pk in selected_ids_db),
            )
            selected_flag = bool(form["selected"].value())
            forms.append((form, selected_flag))
        return forms

    def _prepare_new_unloads(self, instances):
        """Setzt Standard-Status und Barcodes für neue Unloads."""
        for obj in instances:
            if not obj.status:
                obj.status = self.OPEN_STATUS

        BarcodeNumberService.set_barcodes(
            instances,
            prefix=self.BARCODE_PREFIX,
        )

    def _save_new_formset(self, formset, delivery_unit: DeliveryUnit):
        """Speichert neue Unloads und verknüpft sie mit der Liefereinheit."""
        instances = formset.save(commit=False)
        if not instances:
            return

        self._prepare_new_unloads(instances)

        for obj in instances:
            obj.save()
            obj.delivery_units.add(delivery_unit)

        # falls irgendwann can_delete=True wird
        if hasattr(formset, "deleted_objects"):
            for deleted in formset.deleted_objects:
                deleted.delete()

    def _get_success_url(self, delivery_unit_pk: int) -> str:
        """Erfolgs-URL: immer zurück auf die Update-Seite."""
        return reverse("unload_update", kwargs={"delivery_unit_pk": delivery_unit_pk})

    def _get_context_data(self, **kwargs):
        """Basis-Kontext für beide Seiten."""
        formset = kwargs.get("formset")
        context = {
            "delivery_unit": kwargs.get("delivery_unit"),
            "formset": formset,
            "empty_form": formset.empty_form if formset is not None else None,
            "selected_menu": "unload_form",
            "mode": self.mode,  # optional für Template
        }
        context.update(kwargs)
        return context

    def _render(self, request, context):
        """Rendert das passende Template."""
        return render(request, self._template_name(), context)
