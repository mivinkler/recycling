from django.urls import reverse
from django.views.generic.edit import FormView
from django.shortcuts import render, redirect

from warenwirtschaft.forms.unload_form import DeliveryUnitSelectForm
from warenwirtschaft.models import DeliveryUnit, Unload


class UnloadSelectView(FormView):
    template_name = "unload/unload_select.html"
    form_class = DeliveryUnitSelectForm

    # ---------- Hilfsfunktionen ----------

    def _du_queryset(self):
        # Liefert nur aktive Liefereinheiten (is_active=True) – schlanke Feldauswahl.
        return (
            DeliveryUnit.objects
            .filter(is_active=True)
            .only("id", "box_type", "weight", "barcode")
            .order_by("pk")
        )

    def _redirect_by_relation(self, du: DeliveryUnit):
        """
        Regel:
        - Gibt es mind. einen aktiven Unload (is_active=True) mit dieser DU? → Update
        - Sonst → Create
        """
        has_active_unload = Unload.objects.filter(
            is_active=True,
            delivery_units__pk=du.pk
        ).exists()

        viewname = "unload_update" if has_active_unload else "unload_create"
        return redirect(reverse(viewname, kwargs={"delivery_unit_pk": du.pk}))

    # ---------- FormView-Hooks ----------

    def get_form_kwargs(self):
        # Übergibt das QuerySet an das Formular, damit die Auswahl schlank bleibt.
        kwargs = super().get_form_kwargs()
        kwargs["queryset"] = self._du_queryset()
        return kwargs

    def form_valid(self, form):
        # Bei gültiger Auswahl sofort weiterleiten.
        du = form.cleaned_data["delivery_unit"]
        return self._redirect_by_relation(du)

    # ---------- GET/POST ----------

    def get(self, request, *args, **kwargs):
        form = self.get_form()
        if "delivery_unit" in request.GET:
            form = self.form_class(request.GET, queryset=self._du_queryset())
            if form.is_valid():
                return self.form_valid(form)

        vorhandene_unloads = (
            Unload.objects
            .filter(status=1)
            .select_related("material")
            .only("id", "status", "box_type", "weight", "created_at", "material__name")
            .order_by("pk")
        )

        context = {
            "form": form,
            "vorhandene_unloads": vorhandene_unloads,
            "selected_menu": "unload_form",
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST, queryset=self._du_queryset())
        if form.is_valid():
            return self.form_valid(form)
        return render(request, self.template_name, {
            "form": form,
            "selected_menu": "unload_form",
        })
