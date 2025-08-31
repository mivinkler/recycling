# warenwirtschaft/views/unload_create.py
from django.views import View
from django.shortcuts import render, redirect
from django.urls import reverse
from django.db import transaction
import uuid

from warenwirtschaft.models import Unload
from warenwirtschaft.forms.unload_form import (
    DeliveryUnitForm, UnloadFormSet, ExistingEditFormSet
)
from warenwirtschaft.services.barcode_service import BarcodeGenerator


class UnloadCreateView(View):
    template_name = "unload/unload_create.html"

    # ---------- Hilfsabfragen ----------

    def _existing_queryset(self):
        # Nur offene Unloads (Status=1) für den Block 'Vorhandene Wagen'.
        return Unload.objects.filter(status=1).order_by("pk")

    # ---------- GET ----------

    def get(self, request):
        form = DeliveryUnitForm()
        new_fs = UnloadFormSet(queryset=Unload.objects.none(), prefix="new")
        exist_fs = ExistingEditFormSet(queryset=self._existing_queryset(), prefix="exist")
        return self.render_page(form, new_fs, exist_fs)

    # ---------- POST ----------

    def post(self, request):
        form = DeliveryUnitForm(request.POST)
        new_fs = UnloadFormSet(request.POST, queryset=Unload.objects.none(), prefix="new")
        exist_fs = ExistingEditFormSet(request.POST, queryset=self._existing_queryset(), prefix="exist")

        # Kopf (Liefereinheit) muss gültig sein
        if not form.is_valid():
            return self.render_page(form, new_fs, exist_fs)

        delivery_unit = form.cleaned_data["delivery_unit"]

        # Ohne Radio keine Speicherung – fertig.
        selection = request.POST.get("selected_recycling")
        if not selection:
            return self.render_page(form, new_fs, exist_fs)

        # -------- Fall A: Neue Wagen ("new:<prefix>") --------
        if str(selection).startswith("new:"):
            sel_prefix = selection.split(":", 1)[1]
            target = next((f for f in new_fs.forms if f.prefix == sel_prefix), None)

            # Muss existieren, geändert und valide sein
            if not target or not target.has_changed() or not target.is_valid():
                return self.render_page(form, new_fs, exist_fs)

            with transaction.atomic():
                instance = target.save(commit=False)
                self._ensure_barcode(instance)       # Barcode setzen, falls leer
                instance.save()
                self._link_delivery_unit(instance, delivery_unit)
                self._generate_barcode_image(instance)

            # --- Deutsch: Nach dem Speichern auf die Update-Seite der gewählten Liefereinheit weiterleiten ---
            return redirect(reverse("unload_update", kwargs={"pk": delivery_unit.pk}))

        # -------- Fall B: Vorhandene Wagen: ("<pk>") --------
        target = next((f for f in exist_fs.forms if str(f.instance.pk) == str(selection)), None)
        if not target or not target.is_valid():
            return self.render_page(form, new_fs, exist_fs)

        with transaction.atomic():
            instance = target.save()  # speichert Änderungen (falls vorhanden)
            self._link_delivery_unit(instance, delivery_unit)

        # --- Deutsch: Nach dem Speichern auf die Update-Seite der gewählten Liefereinheit weiterleiten ---
        return redirect(reverse("unload_update", kwargs={"delivery_unit_pk": delivery_unit.pk}))

    # ---------- Hilfsmethoden ----------

    def _ensure_barcode(self, unload: Unload) -> None:
        # Falls kein Barcode gesetzt ist, generieren wir einen simplen Code "U<8HEX>".
        if not getattr(unload, "barcode", None):
            suffix = uuid.uuid4().hex[:8].upper()
            unload.barcode = f"U{suffix}"

    def _generate_barcode_image(self, unload: Unload) -> None:
        code = getattr(unload, "barcode", None)
        if not code:
            return
        try:
            BarcodeGenerator(unload, code, "barcodes/unload").generate_image()
        except Exception:
            pass

    def _link_delivery_unit(self, unload: Unload, delivery_unit) -> None:
        # M2M-Verknüpfung: Unload der gewählten Liefereinheit zuordnen.
        if hasattr(unload, "delivery_units"):
            unload.delivery_units.add(delivery_unit)

    # ---------- Rendering ----------

    def render_page(self, form, new_fs, exist_fs):
        return render(self.request, self.template_name, {
            "form": form,
            "formset": new_fs,
            "empty_form": new_fs.empty_form,
            "existing_formset": exist_fs,
            "selected_menu": "unload_create",
        })
