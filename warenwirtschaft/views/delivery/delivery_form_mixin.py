# warenwirtschaft/views/delivery/mixins.py
from warenwirtschaft.forms.delivery_form import get_delivery_unit_formset


class DeliveryFormMixin:
    """
    Gemeinsame Hilfsfunktionen für Delivery-Create/Update:
    - Formset-Erzeugung
    - Kontext-Erweiterung
    - Rendering bei Fehlern
    """

    # Anzahl zusätzlicher leerer Formulare im Formset (Create: 1, Update: 0)
    extra_units = 0

    # ----------------------------------------------------------
    # Formset
    # ----------------------------------------------------------
    def get_units_formset_class(self):
        """Gibt die Formset-Klasse für Liefereinheiten zurück."""
        return get_delivery_unit_formset(extra=self.extra_units)

    def get_units_formset(self):
        """Erstellt das Formset; bei POST/PUT wird es mit Request-Daten gebunden."""
        FormsetClass = self.get_units_formset_class()
        kwargs = {"instance": getattr(self, "object", None)}

        if self.request.method in ("POST", "PUT"):
            kwargs["data"] = self.request.POST

        return FormsetClass(**kwargs)

    # ----------------------------------------------------------
    # Kontext
    # ----------------------------------------------------------
    def get_context_data(self, **kwargs):
        """Erweitert den Kontext um formset/empty_form."""
        context = super().get_context_data(**kwargs)

        formset = kwargs.get("formset") or getattr(self, "formset", None)
        if formset is None:
            formset = self.get_units_formset()

        context["formset"] = formset
        context["empty_form"] = formset.empty_form
        context["selected_menu"] = "delivery_form"
        return context

    def form_invalid(self, form):
        """Rendert Formular + Formset erneut bei Validierungsfehlern."""
        if not hasattr(self, "formset"):
            self.formset = self.get_units_formset()

        return self.render_to_response(
            self.get_context_data(form=form, formset=self.formset)
        )
