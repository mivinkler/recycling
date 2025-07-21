from django.views import View
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.db import transaction

from warenwirtschaft.forms import UnloadChoiceForm, RecyclingFormSet, RecyclingForm
from warenwirtschaft.models import Unload, Recycling


class RecyclingUpdateView(View):
    template_name = "recycling/recycling_update.html"
    success_url = reverse_lazy("recycling_list")

    def get(self, request, pk):
        # Lade bestehende Leerung
        unload = get_object_or_404(Unload, pk=pk)

        # Zeige aktuelle Verknüpfung in der Form
        form = UnloadChoiceForm(initial={"unload": unload})

        # Nur neue Recycling-Einträge im Formset
        formset = RecyclingFormSet(queryset=Recycling.objects.none())

        # Vorhandene aktive Recycling-Objekte anzeigen
        vorhandene_forms = self.build_vorhandene_forms(unload)

        return self.render_page(form, formset, vorhandene_forms, unload)

    def post(self, request, pk):
        unload = get_object_or_404(Unload, pk=pk)

        form = UnloadChoiceForm(request.POST)
        formset = RecyclingFormSet(request.POST, queryset=Recycling.objects.none())
        selected_ids = request.POST.getlist("selected_recycling")

        if form.is_valid() and formset.is_valid():
            with transaction.atomic():
                # Bestehende Verknüpfungen aktualisieren
                for recycling in Recycling.objects.filter(status=1):
                    if str(recycling.pk) in selected_ids:
                        recycling.unloads.add(unload)
                    else:
                        recycling.unloads.remove(unload)

                # Neue Recycling-Einträge speichern und verknüpfen
                new_instances = formset.save(commit=False)
                for instance in new_instances:
                    instance.save()
                    instance.unloads.add(unload)

                # Entfernte Einträge löschen
                for deleted in formset.deleted_objects:
                    deleted.delete()

                # Optional: Status der Unload ändern, wenn nötig
                # unload.status = 3
                # unload.save()

            return redirect(self.success_url)

        # Fehlerfall: Seite neu anzeigen mit Fehlern
        vorhandene_forms = self.build_vorhandene_forms(unload)
        return self.render_page(form, formset, vorhandene_forms, unload)

    def build_vorhandene_forms(self, unload):
        """Baue Formulare für bestehende Recycling-Einträge mit gesetzten Checkboxen."""
        forms = []
        for obj in Recycling.objects.filter(status=1):
            form = RecyclingForm(instance=obj, prefix=f"recycling_{obj.pk}")
            if unload in obj.unloads.all():
                form.fields["selected"].initial = True
            forms.append(form)
        return forms

    def render_page(self, form, formset, vorhandene_forms, unload):
        return render(self.request, self.template_name, {
            "form": form,
            "formset": formset,
            "empty_form": formset.empty_form,
            "vorhandene_forms": vorhandene_forms,
            "unload": unload,
            "selected_menu": "recycling_update",
        })
