# warenwirtschaft/views/delivery/mixins.py
# -*- coding: utf-8 -*-
from django.db import transaction
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy

from warenwirtschaft.models.delivery import Delivery
from warenwirtschaft.forms.delivery_form import DeliveryForm, get_delivery_unit_formset
from warenwirtschaft.services.barcode_number_service import BarcodeNumberService


class DeliveryFormMixin:
    """
    Gemeinsame Logik für Create/Update von Lieferungen und deren Einheiten.

    Aufgaben:
    - Erzeugung und Validierung des Formsets
    - Löschen markierter Liefereinheiten
    - Speichern neuer/aktualisierter Einheiten
    - Optionale automatische Barcode-Erzeugung
    """

    model = Delivery
    form_class = DeliveryForm
    context_object_name = "delivery"
    success_url = reverse_lazy("delivery_list")

    # Anzahl zusätzlicher leerer Formulare (0 bei Update, 1 bei Create)
    extra_units = 0

    # Ob neue Barcodes generiert werden sollen
    generate_barcodes = False
    BARCODE_PREFIX = "L"

    # ----------------------------------------------------------
    # Formset-Erstellung
    # ----------------------------------------------------------
    def get_units_formset_class(self):
        """Gibt die Formset-Klasse für Liefereinheiten zurück."""
        return get_delivery_unit_formset(extra=self.extra_units)

    def get_units_formset(self):
        """Erzeugt das Formset basierend auf der aktuellen Anfrage."""
        FormsetClass = self.get_units_formset_class()
        kwargs = {"instance": getattr(self, "object", None)}

        if self.request.method in ("POST", "PUT"):
            kwargs["data"] = self.request.POST

        return FormsetClass(**kwargs)

    # ----------------------------------------------------------
    # Kontext
    # ----------------------------------------------------------
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        formset = kwargs.get("formset") or getattr(self, "formset", None)
        if formset is None:
            formset = self.get_units_formset()

        context["formset"] = formset
        context["empty_form"] = formset.empty_form
        context["selected_menu"] = "delivery_form"
        return context

    # ----------------------------------------------------------
    # Fehlerschleife
    # ----------------------------------------------------------
    def form_invalid(self, form):
        if not hasattr(self, "formset"):
            self.formset = self.get_units_formset()
        return self.render_to_response(
            self.get_context_data(form=form, formset=self.formset)
        )

    # ----------------------------------------------------------
    # Speichern
    # ----------------------------------------------------------
    def form_valid(self, form):
        self.formset = self.get_units_formset()

        if not self.formset.is_valid():
            return self.form_invalid(form)

        with transaction.atomic():
            # 1) Lieferung speichern
            self.object = form.save()
            self.formset.instance = self.object

            # 2) Markierte Einheiten löschen
            #    inlineformset_factory stellt deleted_forms bereit, nicht deleted_objects
            for deleted_form in self.formset.deleted_forms:
                instance = getattr(deleted_form, "instance", None)
                # Nur echte, bereits gespeicherte Objekte löschen
                if instance and instance.pk:
                    instance.delete()

            # 3) Neue/aktualisierte Einheiten holen
            units = self.formset.save(commit=False)

            # 4) Optional: Barcodes erzeugen
            if self.generate_barcodes:
                for unit in units:
                    val = (unit.barcode or "").strip()
                    if not val:
                        unit.barcode = BarcodeNumberService.make_code(
                            prefix=self.BARCODE_PREFIX
                        )

            # 5) Einheiten speichern
            for unit in units:
                unit.save()

            # 6) M2M-Felder, falls vorhanden
            if hasattr(self.formset, "save_m2m"):
                self.formset.save_m2m()

        return HttpResponseRedirect(self.get_success_url())
