from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View

from warenwirtschaft.models import DeliveryUnit, Unload
from warenwirtschaft.models_common.choices import StatusChoices


class UnloadSelectView(View):
    """
    Auswahl einer Liefereinheit für die Vorsortierung.
    Diese View speichert nichts, sondern leitet nur weiter.
    """

    template_name = "unload/unload_select.html"
    OPEN_STATUS = StatusChoices.VORSORTIERUNG_LAUFEND

    # --------------------------------------------------
    # Hilfsfunktionen
    # --------------------------------------------------
    def _du_queryset(self):
        """
        Liefert alle aktiven Liefereinheiten für die Auswahl.
        """
        return (
            DeliveryUnit.objects
            .filter(is_active=True)
            .only("id", "box_type", "weight", "barcode")
            .order_by("pk")
        )

    def _redirect_by_relation(self, du: DeliveryUnit):
        """
        - Gibt es mind. einen aktiven Unload mit dieser DU? → Update
        - Sonst → Create
        """
        has_active_unload = Unload.objects.filter(
            is_active=True,
            delivery_units__pk=du.pk,
        ).exists()

        viewname = "unload_update" if has_active_unload else "unload_create"
        return redirect(
            reverse(viewname, kwargs={"delivery_unit_pk": du.pk})
        )

    # --------------------------------------------------
    # GET
    # --------------------------------------------------
    def get(self, request, *args, **kwargs):
        delivery_units = self._du_queryset()

        # Wenn eine Auswahl über GET kam → direkt weiterleiten
        du_id = request.GET.get("delivery_unit")
        if du_id:
            try:
                du_pk = int(du_id)
            except ValueError:
                du_pk = None

            if du_pk is not None:
                du = delivery_units.filter(pk=du_pk).first()
                if du is not None:
                    return self._redirect_by_relation(du)
                # Falls keine passende DU gefunden wurde, einfach Seite anzeigen

        context = {
            "delivery_units": delivery_units,
            "selected_menu": "unload_form",
        }
        return render(request, self.template_name, context)
