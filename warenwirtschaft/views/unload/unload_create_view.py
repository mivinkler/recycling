# warenwirtschaft/views/unload_create.py
from django.views import View
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.db import transaction
from django.contrib import messages
import uuid

from warenwirtschaft.models import Unload
from warenwirtschaft.forms_neu.unload_form import (
    DeliveryUnitForm, UnloadFormSet, ExistingEditFormSet
)
from warenwirtschaft.services.barcode_service import BarcodeGenerator


class UnloadCreateView(View):
    template_name = 'unload/unload_create.html'
    success_url = reverse_lazy('unload_list')

    # GET – leere neue Zeile + vorhandene (Status=1)
    def get(self, request):
        form = DeliveryUnitForm()
        formset = UnloadFormSet(queryset=Unload.objects.none(), prefix="new")

        existing_qs = Unload.objects.filter(status=1).order_by('pk')
        existing_formset = ExistingEditFormSet(queryset=existing_qs, prefix="exist")

        return render(request, self.template_name, {
            "form": form,
            "formset": formset,
            "empty_form": formset.empty_form,
            "existing_formset": existing_formset,
        })

    # POST – speichern genau EINE Zeile: entweder eine neue ODER eine bestehende
    def post(self, request):
        form = DeliveryUnitForm(request.POST)
        # Формсеты бадним, но валидируем только нужную форму
        new_formset = UnloadFormSet(request.POST, queryset=Unload.objects.none(), prefix="new")
        existing_qs = Unload.objects.filter(status=1).order_by('pk')
        exist_formset = ExistingEditFormSet(request.POST, queryset=existing_qs, prefix="exist")

        # HINWEIS: In deinem Template heißt das Radio noch "selected_recycling"
        selected_pk = request.POST.get("selected_recycling")

        # Kopf (Liefereinheit) muss stimmen
        if not form.is_valid():
            return render(request, self.template_name, {
                "form": form,
                "formset": new_formset,
                "empty_form": new_formset.empty_form,
                "existing_formset": exist_formset,
            })

        delivery_unit = form.cleaned_data["delivery_unit"]

        # herausfinden, ob Nutzer eine NEUE oder eine BESTEHENDE gewählt hat
        changed_new_forms = []
        for f in new_formset.forms:
            # валидируем только реально заполненные формы
            if f.has_changed():
                if f.is_valid():
                    changed_new_forms.append(f)
                else:
                    # показать ошибки этой конкретной новой формы
                    for field, errs in f.errors.items():
                        for err in errs:
                            new_formset._non_form_errors = new_formset.non_form_errors()  # no-op, just consistency
                    messages.error(request, "Bitte füllen Sie die neue Zeile korrekt aus.")
                    return render(request, self.template_name, {
                        "form": form,
                        "formset": new_formset,
                        "empty_form": new_formset.empty_form,
                        "existing_formset": exist_formset,
                    })

        has_one_new = (len(changed_new_forms) == 1)
        has_existing = bool(selected_pk)

        # Exklusivität prüfen
        if has_one_new and has_existing:
            messages.error(request, "Bitte wählen Sie entweder eine bestehende Zeile ODER erfassen Sie genau eine neue Zeile.")
            return render(request, self.template_name, {
                "form": form,
                "formset": new_formset,
                "empty_form": new_formset.empty_form,
                "existing_formset": exist_formset,
            })
        if not has_one_new and not has_existing:
            messages.error(request, "Bitte wählen Sie genau eine Option: bestehende Zeile oder neue Zeile.")
            return render(request, self.template_name, {
                "form": form,
                "formset": new_formset,
                "empty_form": new_formset.empty_form,
                "existing_formset": exist_formset,
            })
        if len(changed_new_forms) > 1:
            messages.error(request, "Bitte erfassen Sie nur eine neue Zeile gleichzeitig.")
            return render(request, self.template_name, {
                "form": form,
                "formset": new_formset,
                "empty_form": new_formset.empty_form,
                "existing_formset": exist_formset,
            })

        with transaction.atomic():
            if has_one_new:
                f = changed_new_forms[0]
                unload = f.save(commit=False)

                suffix = uuid.uuid4().hex[:8].upper()
                barcode = f"U{suffix}"
                if hasattr(unload, "barcode"):
                    unload.barcode = barcode

                unload.save()           # Erst speichern, dann M2M
                # Liefereinheit aus dem Kopf verknüpfen
                if hasattr(unload, "delivery_units"):
                    unload.delivery_units.add(delivery_unit)

                # Barcode-Bild erzeugen
                try:
                    BarcodeGenerator(unload, barcode, 'barcodes/unload').generate_image()
                except Exception:
                    # Fehler beim Bild – nicht kritisch für die Transaktion
                    pass

            else:
                # Vorhandene Wagen
                target_form = None
                for f in exist_formset.forms:
                    if str(f.instance.pk) == str(selected_pk):
                        target_form = f
                        break

                if not target_form:
                    messages.error(request, "Ausgewählter Wagen wurde nicht gefunden.")
                    return render(request, self.template_name, {
                        "form": form,
                        "formset": new_formset,
                        "empty_form": new_formset.empty_form,
                        "existing_formset": exist_formset,
                    })

                # ein Form (ohne .is_valid() )
                if not target_form.is_valid():
                    messages.error(request, "Bitte füllen Sie die ausgewählte bestehende Zeile korrekt aus.")
                    return render(request, self.template_name, {
                        "form": form,
                        "formset": new_formset,
                        "empty_form": new_formset.empty_form,
                        "existing_formset": exist_formset,
                    })

                instance = target_form.save(commit=True)  # Status & Gewicht übernommen
                if hasattr(instance, "delivery_units"):
                    instance.delivery_units.add(delivery_unit)

        return redirect(self.success_url)
