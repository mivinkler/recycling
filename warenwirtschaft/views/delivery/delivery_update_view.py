from django.db import transaction
from django.views.generic.edit import UpdateView
from django.http import HttpResponseRedirect

from warenwirtschaft.models.delivery import Delivery
from warenwirtschaft.forms.delivery_form import DeliveryForm
from warenwirtschaft.views.delivery.delivery_form_mixin import DeliveryFormMixin


class DeliveryUpdateView(DeliveryFormMixin, UpdateView):
    template_name = "delivery/delivery_update.html"

    model = Delivery
    form_class = DeliveryForm
    context_object_name = "delivery"

    # Beim Update keine zusätzlichen leeren Formulare
    extra_units = 0

    def form_valid(self, form):
        # Formset validieren
        self.formset = self.get_units_formset()
        if not self.formset.is_valid():
            return self.form_invalid(form)

        with transaction.atomic():
            # 1) Lieferung speichern
            self.object = form.save()
            self.formset.instance = self.object

            # 2) Update-spezifisch: gelöschte Einheiten entfernen
            for deleted_form in self.formset.deleted_forms:
                instance = getattr(deleted_form, "instance", None)
                if instance and instance.pk:
                    instance.delete()

            # 3) Units holen (neu/geändert)
            units = self.formset.save(commit=False)

            # 4) Units speichern (keine Barcode-Erzeugung beim Update)
            for unit in units:
                unit.save()

            # 5) M2M speichern (falls vorhanden)
            if hasattr(self.formset, "save_m2m"):
                self.formset.save_m2m()

        # Nach dem Speichern auf derselben Seite bleiben
        return HttpResponseRedirect(self.request.get_full_path())
