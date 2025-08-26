from django.views import View
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.db import transaction
import uuid

from warenwirtschaft.models import Unload, DeliveryUnit
from warenwirtschaft.forms_neu.unload_form import (
    DeliveryUnitForm, UnloadFormSet, ExistingEditFormSet
)
from warenwirtschaft.services.barcode_service import BarcodeGenerator


class UnloadUpdateView(View):
    """
    🇩🇪 Update-Ansicht (Checkbox-Logik):
    - 'Vorhandene Wagen' verwenden Checkboxen: Mehrfach-Verknüpfung möglich.
    - Bereits verknüpfte Zeilen bleiben bedienbar (data-keep-enabled-row), Lock-Icon bleibt zu.
    - 'Neue Wagen' wie im Create: neue Zeile speichern und verknüpfen, wenn Checkbox markiert.
    - 'Liefereinheiten' ist reine Anzeige (keine Eingabe/Validierung).
    """
    template_name = "unload/unload_update.html"

    # ---------- GET ----------

    def get(self, request, pk: int):
        delivery_unit = get_object_or_404(DeliveryUnit, pk=pk)

        # 🇩🇪 Nur zur Anzeige, nicht zum Ausfüllen/Validieren
        form = DeliveryUnitForm(initial={"delivery_unit": delivery_unit})
        new_fs = UnloadFormSet(queryset=Unload.objects.none(), prefix="new")
        exist_fs = ExistingEditFormSet(queryset=self._existing_queryset(), prefix="exist")

        return self.render_page(request, form, new_fs, exist_fs, delivery_unit)

    # ---------- POST ----------

    def post(self, request, pk: int):
        delivery_unit = get_object_or_404(DeliveryUnit, pk=pk)

        # 🇩🇪 NICHT binden! Feld ist read-only und kommt nicht im POST.
        form = DeliveryUnitForm(initial={"delivery_unit": delivery_unit})
        new_fs = UnloadFormSet(request.POST, queryset=Unload.objects.none(), prefix="new")
        exist_qs = self._existing_queryset()
        exist_fs = ExistingEditFormSet(request.POST, queryset=exist_qs, prefix="exist")

        # 🇩🇪 Auswahl aus Checkboxen
        selected_vals = request.POST.getlist("selected_recycling")
        selected_existing_ids = {int(v) for v in selected_vals if v.isdigit()}
        selected_new_prefixes = [v.split(":", 1)[1] for v in selected_vals if v.startswith("new:")]

        linked_ids = self._linked_ids(delivery_unit)
        to_add = selected_existing_ids - linked_ids
        to_remove = linked_ids - selected_existing_ids

        with transaction.atomic():
            # 1) Bestehende Formulare (z. B. Gewicht/Status) sichern
            for f in exist_fs.forms:
                if f.has_changed() and f.is_valid():
                    f.save()

            # 2) Verknüpfungen für bestehende Unloads hinzufügen/entfernen
            for pk_ in to_add:
                unload = next((u for u in exist_qs if u.pk == pk_), None) or get_object_or_404(Unload, pk=pk_)
                self._link(unload, delivery_unit)

            for pk_ in to_remove:
                unload = next((u for u in exist_qs if u.pk == pk_), None) or get_object_or_404(Unload, pk=pk_)
                self._unlink(unload, delivery_unit)

            # 3) Ausgewählte NEUE Zeilen speichern und verknüpfen
            for f in new_fs.forms:
                if f.prefix in selected_new_prefixes:
                    if f.is_valid() and f.has_changed():
                        instance = f.save(commit=False)
                        self._ensure_barcode(instance)
                        instance.save()
                        self._link(instance, delivery_unit)
                        self._barcode_img(instance)
                    else:
                        if not f.is_valid():
                            return self.render_page(request, form, new_fs, exist_fs, delivery_unit)

        return redirect(self._success_url(delivery_unit))

    # ---------- Helfer ----------

    def _existing_queryset(self):
        """🇩🇪 Nur offene Unloads (Status=1) für 'Vorhandene Wagen'."""
        return Unload.objects.filter(status=1).order_by("pk")

    def _linked_ids(self, delivery_unit):
        """🇩🇪 IDs der aktuell mit der Liefereinheit verknüpften Unloads."""
        return set(
            Unload.objects.filter(delivery_units=delivery_unit).values_list("id", flat=True)
        )

    def _ensure_barcode(self, unload: Unload) -> None:
        """🇩🇪 Falls kein Barcode: 'U<8HEX>' generieren."""
        if not getattr(unload, "barcode", None):
            unload.barcode = f"U{uuid.uuid4().hex[:8].upper()}"

    def _barcode_img(self, unload: Unload) -> None:
        """🇩🇪 Barcode-Bild erzeugen (best effort)."""
        code = getattr(unload, "barcode", None)
        if not code:
            return
        try:
            BarcodeGenerator(unload, code, "barcodes/unload").generate_image()
        except Exception:
            pass

    def _link(self, unload: Unload, delivery_unit: DeliveryUnit) -> None:
        """🇩🇪 M2M-Verknüpfung hinzufügen."""
        if hasattr(unload, "delivery_units"):
            unload.delivery_units.add(delivery_unit)

    def _unlink(self, unload: Unload, delivery_unit: DeliveryUnit) -> None:
        """🇩🇪 M2M-Verknüpfung entfernen."""
        if hasattr(unload, "delivery_units"):
            unload.delivery_units.remove(delivery_unit)

    def _success_url(self, delivery_unit: DeliveryUnit) -> str:
        """🇩🇪 Nach dem Speichern zurück auf dieselbe Update-Seite."""
        return reverse("unload_update", kwargs={"pk": delivery_unit.pk})

    # ---------- Rendering ----------

    def render_page(self, request, form, new_fs, exist_fs, delivery_unit):
        """
        🇩🇪 Einheitliches Rendering:
        - linked_ids: damit das Template verknüpfte Checkboxen als 'checked' markiert
                      und Zeilen/Inputs mit data-keep-enabled(-row) versieht.
        """
        context = {
            "form": form,
            "formset": new_fs,
            "empty_form": new_fs.empty_form,
            "existing_formset": exist_fs,
            "delivery_unit": delivery_unit,
            "linked_ids": self._linked_ids(delivery_unit),
            "selected_menu": "unload_update",
        }
        return render(request, self.template_name, context)
