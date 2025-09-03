# warenwirtschaft/views/unload_update.py
from __future__ import annotations

import uuid
from django.views import View
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.db import transaction

from warenwirtschaft.models import Unload, DeliveryUnit
from warenwirtschaft.forms.unload_form import UnloadFormSet, ExistingEditFormSet
from warenwirtschaft.services.barcode_service import BarcodeGenerator


class UnloadUpdateView(View):
    """
    🇩🇪 Update-Ansicht:
    - Checkboxen erlauben Mehrfachauswahl (bestehende + neue Zeilen).
    - GET kann vorgewählte Checkboxen über Query-String (selected_recycling=...) mitbringen.
      Diese werden zusätzlich zu bereits verknüpften Unloads als checked angezeigt.
    - POST speichert:
        * geänderte Felder der bestehenden Zeilen (Status/Gewicht)
        * M2M-Verknüpfungen (hinzufügen/entfernen) gemäß Checkboxen
        * ausgewählte neue Zeilen (nur wenn geändert & gültig), inkl. Barcode
    """
    template_name = "unload/unload_update.html"
    OPEN_STATUS = 1  # 🇩🇪 Lesbarer statt magischer Zahl

    # ---------- Datenbeschaffung ----------

    def _existing_queryset(self):
        """
        🇩🇪 Nur offene Unloads für 'Aktive Wagen'.
        .only(...) reduziert die Feldmenge (leichter für DB/Serializer).
        """
        return (
            Unload.objects
            .filter(status=self.OPEN_STATUS)
            .only("pk", "material", "box_type", "status", "weight")
            .order_by("pk")
        )

    # ---------- Formset-Fabrik ----------

    def _build_formsets(self, data=None):
        """
        🇩🇪 Einheitliche Erzeugung der Formsets (keine Duplikation in GET/POST).
        """
        new_fs = UnloadFormSet(data=data, queryset=Unload.objects.none(), prefix="new")
        exist_fs = ExistingEditFormSet(data=data, queryset=self._existing_queryset(), prefix="exist")
        return new_fs, exist_fs

    # ---------- GET ----------

    def get(self, request, delivery_unit_pk: int):
        """
        🇩🇪 GET zeigt:
        - bereits verknüpfte Unloads als checked
        - zusätzlich per Query-String vorgewählte Checkboxen
        """
        delivery_unit = get_object_or_404(DeliveryUnit, pk=delivery_unit_pk)
        new_fs, exist_fs = self._build_formsets()

        # Vorwahlen aus der URL: selected_recycling=... (mehrfach erlaubt)
        tokens = request.GET.getlist("selected_recycling")

        # 🇩🇪 Existierende IDs: Union aus bereits verknüpften + GET-Vorwahl
        linked_ids = self._linked_ids(delivery_unit)
        prechecked_exist = {int(t) for t in tokens if str(t).isdigit()}
        linked_or_prechecked = linked_ids | prechecked_exist

        # 🇩🇪 Vorwahl für NEUE Zeilen (Prefixe wie 'new:<prefix>')
        prechecked_new_prefixes = [t.split(":", 1)[1] for t in tokens if str(t).startswith("new:")]

        return self._render(
            delivery_unit=delivery_unit,
            new_fs=new_fs,
            exist_fs=exist_fs,
            linked_ids=linked_or_prechecked,
            prechecked_new_prefixes=prechecked_new_prefixes,
        )

    # ---------- POST ----------

    def post(self, request, delivery_unit_pk: int):
        """
        🇩🇪 POST übernimmt nur das, was der Nutzer wirklich ausgewählt/geändert hat:
        - Validierung nur ausgewählter NEUER und geänderter BESTEHENDER Zeilen
        - M2M wird aus dem Checkbox-Snapshot (POST) berechnet
        """
        delivery_unit = get_object_or_404(DeliveryUnit, pk=delivery_unit_pk)
        new_fs, exist_fs = self._build_formsets(data=request.POST)

        # 🇩🇪 Auswahl der Checkboxen (Snapshot)
        tokens = request.POST.getlist("selected_recycling")

        # Schneller Zugriff: Maps für O(1)-Lookups
        new_map = {f.prefix: f for f in new_fs.forms}
        exist_map = {str(f.instance.pk): f for f in exist_fs.forms}

        # 🇩🇪 Ausgewählte NEUE Formulare (nur geänderte)
        selected_new = [
            new_map.get(t.split(":", 1)[1])
            for t in tokens if str(t).startswith("new:")
        ]
        selected_new = [f for f in selected_new if f and f.has_changed()]

        # 🇩🇪 Bestehende: ID-Snapshot aus POST
        selected_exist_ids = {
            int(t) for t in tokens if str(t).isdigit()
        }

        # 🇩🇪 Validierung: nur das Nötigste
        changed_exist = [f for f in exist_fs.forms if f.has_changed()]
        if not all(f.is_valid() for f in [*selected_new, *changed_exist]):
            # Bei Fehlern neu rendern: bereits verknüpfte IDs bleiben gesetzt
            return self._render(
                delivery_unit=delivery_unit,
                new_fs=new_fs,
                exist_fs=exist_fs,
                linked_ids=self._linked_ids(delivery_unit),
                prechecked_new_prefixes=[],  # POST-Fehlerfall: Template liest Werte direkt aus Bound-Formen
            )

        # 🇩🇪 Diff der M2M-Verknüpfung berechnen
        linked_before = self._linked_ids(delivery_unit)
        to_add = selected_exist_ids - linked_before
        to_remove = linked_before - selected_exist_ids

        # 🇩🇪 Für effizienten Zugriff evtl. vorhandene Instanzen aus exist_fs nehmen
        exist_cache = {f.instance.pk: f.instance for f in exist_fs.forms}

        # ---------- Speichern: alles oder nichts ----------
        with transaction.atomic():
            # 1) Bestehende geänderte Zeilen sichern
            for f in changed_exist:
                f.save()

            # 2) M2M hinzufügen/entfernen gemäß Checkboxen
            for pk_ in to_add:
                unload = exist_cache.get(pk_) or get_object_or_404(Unload, pk=pk_)
                self._link(unload, delivery_unit)

            for pk_ in to_remove:
                unload = exist_cache.get(pk_) or get_object_or_404(Unload, pk=pk_)
                self._unlink(unload, delivery_unit)

            # 3) Neue ausgewählte Zeilen speichern + verknüpfen
            for f in selected_new:
                instance: Unload = f.save(commit=False)
                self._ensure_barcode(instance)  # Barcode setzen, falls leer
                instance.save()
                self._link(instance, delivery_unit)
                self._generate_barcode_image(instance)

        return redirect(self._success_url(delivery_unit.pk))

    # ---------- Hilfsmethoden ----------

    def _linked_ids(self, delivery_unit: DeliveryUnit) -> set[int]:
        """
        🇩🇪 Liefert die IDs der Unloads, die aktuell mit der Liefereinheit verknüpft sind.
        """
        return set(
            Unload.objects.filter(delivery_units=delivery_unit).values_list("id", flat=True)
        )

    def _ensure_barcode(self, unload: Unload) -> None:
        """
        🇩🇪 Falls kein Barcode gesetzt ist, generieren wir ein einfaches Muster „U<8HEX>“.
        """
        if not getattr(unload, "barcode", None):
            unload.barcode = f"U{uuid.uuid4().hex[:8].upper()}"

    def _generate_barcode_image(self, unload: Unload) -> None:
        """
        🇩🇪 Bildgenerierung ist 'best effort' – Fehler blockieren den Vorgang nicht.
        """
        code = getattr(unload, "barcode", None)
        if not code:
            return
        try:
            BarcodeGenerator(unload, code, "barcodes/unload").generate_image()
        except Exception:
            pass  # Optional: Logging ergänzen

    def _link(self, unload: Unload, delivery_unit: DeliveryUnit) -> None:
        """🇩🇪 M2M-Verknüpfung hinzufügen."""
        if hasattr(unload, "delivery_units"):
            unload.delivery_units.add(delivery_unit)

    def _unlink(self, unload: Unload, delivery_unit: DeliveryUnit) -> None:
        """🇩🇪 M2M-Verknüpfung entfernen."""
        if hasattr(unload, "delivery_units"):
            unload.delivery_units.remove(delivery_unit)

    def _success_url(self, delivery_unit_pk: int) -> str:
        """🇩🇪 Nach dem Speichern zurück auf dieselbe Update-Seite."""
        return reverse("unload_update", kwargs={"delivery_unit_pk": delivery_unit_pk})

    def _render(self, delivery_unit, new_fs, exist_fs, linked_ids: set[int], prechecked_new_prefixes=None):
        """
        🇩🇪 Zentrales Rendering:
        - linked_ids: für bestehende Zeilen, die als 'checked' erscheinen sollen
        - prechecked_new_prefixes: optionale Vorwahl für neue Zeilen (nur GET)
        """
        return render(
            self.request,
            self.template_name,
            {
                "formset": new_fs,
                "empty_form": new_fs.empty_form,
                "existing_formset": exist_fs,
                "delivery_unit": delivery_unit,
                "linked_ids": linked_ids,
                "prechecked_new_prefixes": prechecked_new_prefixes or [],
                "selected_menu": "unload_update",
            },
        )
