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
    Gemeinsamer Screen für Create + Update der Vorsortierung
    einer DeliveryUnit.

    - Ein URL
    - Ein Template
    - Zwei Aktionen:
      1) Vorsortierung speichern
      2) Entladung abschließen (DeliveryUnit deaktivieren)
    """

    template_name = "unload/unload_create.html"

    # Status für offene Unloads
    OPEN_STATUS = StatusChoices.IN_VORSORTIERUNG

    # Prefix für generierte Barcodes
    BARCODE_PREFIX = "S"

    # Prefix für das Formset neuer Unloads
    NEW_PREFIX = "new"

    # ----------------------------------------------------------
    # GET
    # ----------------------------------------------------------
    def get(self, request, delivery_unit_pk: int):
        """
        Zeigt die Vorsortierungsseite an:
        - bestehende (aktive) Unloads
        - neue Unloads (Formset)
        """
        delivery_unit = get_object_or_404(DeliveryUnit, pk=delivery_unit_pk)
        context = self._build_context(delivery_unit)
        return render(request, self.template_name, context)

    # ----------------------------------------------------------
    # POST
    # ----------------------------------------------------------
    def post(self, request, delivery_unit_pk: int):
        """
        Verarbeitet Formular-Submits:
        - action=finish_unload  -> Entladung abschließen
        - sonst                -> Vorsortierung speichern
        """
        delivery_unit = get_object_or_404(DeliveryUnit, pk=delivery_unit_pk)

        # 1) Entladung abschließen
        if request.POST.get("action") == "finish_unload":
            delivery_unit.is_active = False
            # save() triggert automatisch das Setzen von inactive_at (Mixin)
            delivery_unit.save()

            messages.success(request, "Entladung erfolgreich abgeschlossen.")
            return redirect("delivery_list")

        # 2) Normales Speichern der Vorsortierung

        # Formset für neue Unloads
        new_formset = UnloadFormSet(
            data=request.POST,
            queryset=Unload.objects.none(),
            prefix=self.NEW_PREFIX,
        )

        # Einzel-Forms für bestehende Unloads
        vorhandene_forms = self._build_existing_forms(
            delivery_unit,
            data=request.POST,
        )

        # Validierung
        if not new_formset.is_valid() or not all(f.is_valid() for f, _ in vorhandene_forms):
            messages.error(request, "⚠️ Bitte Eingaben prüfen.")
            return render(
                request,
                self.template_name,
                self._build_context(delivery_unit, new_formset, vorhandene_forms),
            )

        # IDs der ausgewählten bestehenden Unloads
        selected_ids = {
            str(f.instance.pk)
            for f, _ in vorhandene_forms
            if f.cleaned_data.get("selected")
        }

        # Alle Änderungen in einer Transaktion
        with transaction.atomic():
            # 1) Geänderte bestehende Unloads speichern
            for f, _ in vorhandene_forms:
                if f.has_changed():
                    f.save()

            # 2) M2M-Verknüpfung DeliveryUnit <-> Unload synchronisieren
            for obj in self._open_unloads_qs():
                if str(obj.pk) in selected_ids:
                    obj.delivery_units.add(delivery_unit)
                else:
                    obj.delivery_units.remove(delivery_unit)

            # 3) Neue Unloads speichern, Barcode setzen und verknüpfen
            self._save_new(new_formset, delivery_unit)

        messages.success(request, "✅ Die Daten sind gespeichert.")
        return redirect(
            reverse("unload_create", kwargs={"delivery_unit_pk": delivery_unit.pk})
        )

    # ----------------------------------------------------------
    # Helper-Methoden
    # ----------------------------------------------------------

    def _build_context(self, delivery_unit, new_formset=None, vorhandene_forms=None):
        """
        Baut den Kontext für GET und POST (bei Fehlern).
        """
        if new_formset is None:
            new_formset = UnloadFormSet(
                queryset=Unload.objects.none(),
                prefix=self.NEW_PREFIX,
            )

        if vorhandene_forms is None:
            vorhandene_forms = self._build_existing_forms(delivery_unit)

        return {
            "delivery_unit": delivery_unit,
            "formset": new_formset,
            "vorhandene_forms": vorhandene_forms,
            "empty_form": new_formset.empty_form,
            "selected_menu": "unload_form",
        }

    def _open_unloads_qs(self):
        """
        Liefert alle offenen, aktiven Unloads,
        die für die Vorsortierung relevant sind.
        """
        return (
            Unload.objects
            .filter(is_active=True, status=self.OPEN_STATUS)
            .order_by("pk")
        )

    def _build_existing_forms(self, delivery_unit: DeliveryUnit, data=None):
        """
        Erstellt Einzel-Forms für alle offenen Unloads.

        - Checkbox 'selected' zeigt, ob der Unload
          bereits mit der DeliveryUnit verknüpft ist
        """
        ExistingEditForm = ExistingEditFormSet.form

        # IDs der aktuell verknüpften Unloads
        selected_ids_db = set(
            Unload.objects
            .filter(delivery_units=delivery_unit, is_active=True)
            .values_list("pk", flat=True)
        )

        result = []
        for obj in self._open_unloads_qs():
            form = ExistingEditForm(
                data=data,
                instance=obj,
                prefix=f"exist_{obj.pk}",
                selected_initial=(obj.pk in selected_ids_db),
            )
            result.append((form, bool(form["selected"].value())))
        return result

    def _save_new(self, formset, delivery_unit: DeliveryUnit):
        """
        Speichert neue Unloads:
        - setzt Standard-Status
        - generiert Barcodes
        - verknüpft mit DeliveryUnit
        """
        instances = formset.save(commit=False)
        if not instances:
            return

        for obj in instances:
            if not obj.status:
                obj.status = self.OPEN_STATUS

        BarcodeNumberService.set_barcodes(
            instances,
            prefix=self.BARCODE_PREFIX,
        )

        for obj in instances:
            obj.save()
            obj.delivery_units.add(delivery_unit)
