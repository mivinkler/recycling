# warenwirtschaft/views/unload_create.py
from __future__ import annotations

import uuid
from django.views import View
from django.shortcuts import render, redirect
from django.urls import reverse
from django.db import transaction

from warenwirtschaft.models import Unload
from warenwirtschaft.forms.unload_form import (
    DeliveryUnitForm, UnloadFormSet, ExistingEditFormSet
)
from warenwirtschaft.services.barcode_service import BarcodeGenerator


class UnloadCreateView(View):
    template_name = "unload/unload_create.html"
    OPEN_STATUS = 1  # Lesbarkeit: magischer Wert -> Konstante

    # ---------- Datenbeschaffung ----------

    def _existing_queryset(self):
        """
        Nur offene Unloads für den Block „Aktive Wagen“ laden.
        .only(...) reduziert die übertragenen Felder und DB-Last.
        """
        return (
            Unload.objects
            .filter(status=self.OPEN_STATUS)
            .only("pk", "material", "box_type", "status", "weight")
            .order_by("pk")
        )

    # ---------- Form-Fabrik ----------

    def _build_forms(self, data=None):
        """
        Erzeugt Kopf-Form und beide Formsets einheitlich.
        So vermeiden wir Wiederholung in GET/POST.
        """
        form = DeliveryUnitForm(data=data)
        new_fs = UnloadFormSet(data=data, queryset=Unload.objects.none(), prefix="new")
        exist_fs = ExistingEditFormSet(data=data, queryset=self._existing_queryset(), prefix="exist")
        return form, new_fs, exist_fs

    # ---------- GET ----------

    def get(self, request):
        form, new_fs, exist_fs = self._build_forms()
        return self._render(form, new_fs, exist_fs)

    # ---------- POST ----------

    def post(self, request):
        form, new_fs, exist_fs = self._build_forms(data=request.POST)

        # Kopf (Liefereinheit) muss gültig sein – ohne sie speichern wir nichts.
        if not form.is_valid():
            return self._render(form, new_fs, exist_fs)

        delivery_unit = form.cleaned_data["delivery_unit"]

        # Checkboxen: alle markierten Tokens einlesen; keine Auswahl => Seite neu.
        tokens = request.POST.getlist("selected_recycling")
        if not tokens:
            return self._render(form, new_fs, exist_fs)

        # Für O(1)-Zugriff Form-Maps bauen. Unbekannte Tokens werden einfach ignoriert.
        new_map = {f.prefix: f for f in new_fs.forms}
        exist_map = {str(f.instance.pk): f for f in exist_fs.forms}

        # Auswahl in „neu“ und „bestehend“ aufteilen.
        selected_new = []
        selected_exist = []
        for t in tokens:
            if t.startswith("new:"):
                selected_new.append(new_map.get(t.split(":", 1)[1]))
            else:
                selected_exist.append(exist_map.get(str(t)))

        # None (unbekannte Tokens) herausfiltern, neue, nicht veränderte Zeilen überspringen.
        selected_new = [f for f in selected_new if f and f.has_changed()]
        selected_exist = [f for f in selected_exist if f]

        # Validieren nur der ausgewählten Formulare – schneller und klarer.
        if not all(f.is_valid() for f in [*selected_new, *selected_exist]):
            return self._render(form, new_fs, exist_fs)

        # Atomar speichern: entweder alles oder nichts.
        with transaction.atomic():
            for f in selected_new:
                instance: Unload = f.save(commit=False)
                self._ensure_barcode(instance)   # Barcode setzen, falls leer
                instance.save()
                self._link_delivery_unit(instance, delivery_unit)
                self._generate_barcode_image(instance)

            for f in selected_exist:
                instance: Unload = f.save()      # speichert Änderungen (falls vorhanden)
                self._link_delivery_unit(instance, delivery_unit)

        # Einheitlicher Redirect (passt den kwarg an eure URL an, falls nötig).
        return self._redirect_to_update(delivery_unit.pk)

    # ---------- Hilfsmethoden ----------

    def _redirect_to_update(self, delivery_unit_pk: int):
        """
        Nach erfolgreichem Speichern zur Detail-/Update-Seite der gewählten Liefereinheit.
        """
        return redirect(reverse("unload_update", kwargs={"pk": delivery_unit_pk}))

    def _ensure_barcode(self, unload: Unload) -> None:
        """
        Falls kein Barcode gesetzt ist, generieren wir ein einfaches Muster „U<8HEX>“.
        """
        if not getattr(unload, "barcode", None):
            suffix = uuid.uuid4().hex[:8].upper()
            unload.barcode = f"U{suffix}"

    def _generate_barcode_image(self, unload: Unload) -> None:
        """
        Bildgenerierung ist „best effort“ – Fehler hier sollen den Speichervorgang nicht blockieren.
        """
        code = getattr(unload, "barcode", None)
        if not code:
            return
        try:
            BarcodeGenerator(unload, code, "barcodes/unload").generate_image()
        except Exception:
            # Optional: Logging einführen, wenn nötig.
            pass

    def _link_delivery_unit(self, unload: Unload, delivery_unit) -> None:
        """
        M2M-Verknüpfung: Unload der gewählten Liefereinheit zuordnen.
        """
        if hasattr(unload, "delivery_units"):
            unload.delivery_units.add(delivery_unit)

    # ---------- Rendering ----------

    def _render(self, form, new_fs, exist_fs):
        """
        Zentrales Rendering – vermeidet Duplikate und hält GET/POST schlank.
        """
        return render(self.request, self.template_name, {
            "form": form,
            "formset": new_fs,
            "empty_form": new_fs.empty_form,
            "existing_formset": exist_fs,
            "selected_menu": "unload_create",
        })
