# -*- coding: utf-8 -*-
from django.views import View
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.db import transaction
from django.contrib import messages
from django.db.models import Q
import uuid

from warenwirtschaft.models import Unload, DeliveryUnit
from warenwirtschaft.forms_neu.unload_form import (
    DeliveryUnitForm, UnloadFormSet, ExistingEditFormSet
)
from warenwirtschaft.services.barcode_service import BarcodeGenerator


class UnloadUpdateView(View):
    """
    DE:
    - Auswahl der Liefereinheit oben (DeliveryUnitForm).
    - "Neue Wagen": UnloadFormSet (neue Unloads werden nach save() mit der gewählten Einheit verknüpft).
    - "Vorhandene Wagen": alle Unloads mit Status=1; Checkbox = Verknüpfung + Bearbeitung.
    - M2M-Feld: Unload.delivery_units.
    - WICHTIG: Die gewählte Liefereinheit (aus URL pk oder Formular) wird dem Feld-QuerySet
      hinzugefügt, auch wenn sie nicht status=1 ist, damit sie im Select angezeigt wird und
      die Zuordnung (Prechecked) funktioniert.
    """
    template_name = 'unload/unload_update.html'
    success_url = reverse_lazy('unload_list')

    # --- Hilfsfunktionen -----------------------------------------------------

    def _ensure_du_queryset_includes(self, form: DeliveryUnitForm, unit_id: int | None):
        """DE: Sorgt dafür, dass das Feld 'delivery_unit' die gewünschte Einheit im QuerySet enthält."""
        base_qs = DeliveryUnit.objects.filter(status=1)
        if unit_id:
            form.fields['delivery_unit'].queryset = DeliveryUnit.objects.filter(
                Q(status=1) | Q(pk=unit_id)
            )
        else:
            form.fields['delivery_unit'].queryset = base_qs

    def _prechecked_ids(self, unit: DeliveryUnit | None):
        """DE: IDs der Unloads, die bereits mit der Liefereinheit verknüpft sind (M2M)."""
        if not unit:
            return set()
        return set(
            Unload.objects.filter(delivery_units=unit).values_list('pk', flat=True)
        )

    # --- GET -----------------------------------------------------------------

    def get(self, request, pk=None):
        # DE: Vorauswahl aus URL (optional)
        initial = {"delivery_unit": pk} if pk else None
        form = DeliveryUnitForm(request.GET or None, initial=initial)

        unit = None
        if form.is_valid():
            unit = form.cleaned_data['delivery_unit']
            # DE: Sicherstellen, dass der Select die gewählte Einheit im QuerySet hat
            self._ensure_du_queryset_includes(form, unit_id=unit.pk)
        elif pk:
            # DE: pk aus URL erzwingen (auch wenn status != 1)
            unit = get_object_or_404(DeliveryUnit, pk=pk)
            form = DeliveryUnitForm(initial={"delivery_unit": unit})
            self._ensure_du_queryset_includes(form, unit_id=unit.pk)
        else:
            # DE: Keine Auswahl -> nur aktive Einheiten im Select
            self._ensure_du_queryset_includes(form, unit_id=None)

        # DE: Neue Unloads (leer)
        formset = UnloadFormSet(queryset=Unload.objects.none(), prefix="new")
        if unit:
            # DE: Einheit in neuen Zeilen vorbelegen (komfortabel)
            for f in formset.forms:
                f.initial.setdefault("delivery_units", [unit.pk])

        # DE: Vorhandene Unloads (z.B. alle mit Status=1)
        existing_qs = Unload.objects.filter(status=1).order_by('pk')
        existing_formset = ExistingEditFormSet(queryset=existing_qs, prefix="exist")

        # DE: Bereits verknüpfte Unloads für Checkbox-Precheck
        prechecked_ids = self._prechecked_ids(unit)

        return render(request, self.template_name, {
            "form": form,
            "unit": unit,
            "formset": formset,
            "empty_form": formset.empty_form,
            "existing_qs": existing_qs,
            "existing_formset": existing_formset,
            "prechecked_ids": prechecked_ids,
        })

    # --- POST ----------------------------------------------------------------

    def post(self, request, pk=None):
        form = DeliveryUnitForm(request.POST)

        # DE: Falls im POST eine Einheit kommt, расширим queryset поля, чтобы валидация прошла
        posted_id = request.POST.get('delivery_unit')
        if posted_id:
            try:
                posted_id_int = int(posted_id)
            except ValueError:
                posted_id_int = None
        else:
            posted_id_int = None
        self._ensure_du_queryset_includes(form, unit_id=posted_id_int)

        formset = UnloadFormSet(request.POST, queryset=Unload.objects.none(), prefix="new")

        existing_qs = Unload.objects.filter(status=1).order_by('pk')
        existing_formset = ExistingEditFormSet(request.POST, queryset=existing_qs, prefix="exist")

        # DE: Einziger Checkbox-Parameter: ausgewählte Unloads
        raw_ids = request.POST.getlist("selected_unloads")
        selected_ids_for_link = set()
        for s in raw_ids:
            try:
                selected_ids_for_link.add(int(s))
            except (TypeError, ValueError):
                pass

        if not form.is_valid():
            # DE: Ohne gültige Einheit – erneut rendern
            return render(request, self.template_name, {
                "form": form, "unit": None,
                "formset": formset, "empty_form": formset.empty_form,
                "existing_qs": existing_qs,
                "existing_formset": existing_formset,
                "prechecked_ids": set(),
            })

        if formset.is_valid() and existing_formset.is_valid():
            unit = form.cleaned_data['delivery_unit']

            with transaction.atomic():
                # === Neue Unloads anlegen und mit Einheit verknüpfen ===
                for subform in formset:
                    if not subform.cleaned_data:
                        continue
                    unload = subform.save(commit=False)
                    # DE: Code generieren
                    suffix = uuid.uuid4().hex[:8].upper()
                    code = f"U{suffix}"
                    unload.code = code
                    unload.save()
                    # DE: Barcode generieren
                    BarcodeGenerator(unload, code, 'barcodes/unload').generate_image()
                    # DE: M2M-Verknüpfung
                    unload.delivery_units.add(unit)

                # === Bestehende (angekreuzte) Zeilen speichern (status/weight) ===
                for f in existing_formset.forms:
                    if f.instance.pk in selected_ids_for_link:
                        f.save()

                # === M2M-Verknüpfungen synchronisieren ===
                currently_linked = self._prechecked_ids(unit)
                to_unlink = currently_linked - selected_ids_for_link
                to_link = selected_ids_for_link - currently_linked

                if to_unlink:
                    for u in Unload.objects.filter(pk__in=to_unlink):
                        u.delivery_units.remove(unit)

                if to_link:
                    for u in Unload.objects.filter(pk__in=to_link):
                        u.delivery_units.add(unit)

            messages.success(request, "Vorsortierung wurde aktualisiert.")
            return redirect(self.success_url)

        # DE: Bei Fehlern – Checkboxen beibehalten
        unit = form.cleaned_data.get('delivery_unit') if form.is_valid() else None
        prechecked_ids = selected_ids_for_link if unit else set()

        return render(request, self.template_name, {
            "form": form,
            "unit": unit,
            "formset": formset,
            "empty_form": formset.empty_form,
            "existing_qs": existing_qs,
            "existing_formset": existing_formset,
            "prechecked_ids": prechecked_ids,
        })
