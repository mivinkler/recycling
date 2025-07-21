from django.views import View
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.db import transaction

from warenwirtschaft.forms import UnloadChoiceForm, RecyclingFormSet, RecyclingForm
from warenwirtschaft.models import Unload, Recycling


class RecyclingCreateView(View):
    template_name = "recycling/recycling_create.html"
    success_url = reverse_lazy("recycling_list")

    def get(self, request):
        # Formular für die Auswahl einer Leerung
        form = UnloadChoiceForm()
        formset = RecyclingFormSet(queryset=Recycling.objects.none())

        # Bereits vorhandene Recycling-Objekte (Status = aktiv)
        vorhandene_forms = [
            RecyclingForm(instance=obj, prefix=f"recycling_{obj.pk}")
            for obj in Recycling.objects.filter(status=1)
        ]

        return self.render_page(form, formset, vorhandene_forms)

    def post(self, request):
        unload_form = UnloadChoiceForm(request.POST)
        formset = RecyclingFormSet(request.POST, queryset=Recycling.objects.none())
        selected_ids = request.POST.getlist("selected_recycling")

        if unload_form.is_valid() and formset.is_valid():
            unload = unload_form.cleaned_data["unload"]

            with transaction.atomic():
                # Bestehende Verknüpfungen aktualisieren
                for recycling in Recycling.objects.filter(status=1):
                    if str(recycling.pk) in selected_ids:
                        recycling.unloads.add(unload)
                    else:
                        recycling.unloads.remove(unload)

                # Neue Einträge speichern und mit unload verknüpfen
                new_instances = formset.save(commit=False)
                for instance in new_instances:
                    instance.save()
                    instance.unloads.add(unload)

                # Gelöschte Einträge löschen
                for deleted in formset.deleted_objects:
                    deleted.delete()

                # ✅ Markiere unload als erledigt
                unload.status = 2
                unload.save()

            return redirect(self.success_url)

        # Fehlerfall: Seite mit Fehlern neu anzeigen
        vorhandene_forms = self.build_vorhandene_forms(self.get_selected_unload(request))
        return self.render_page(unload_form, formset, vorhandene_forms)


    def render_page(self, form, formset, vorhandene_forms):
        return render(self.request, self.template_name, {
            "form": form,
            "formset": formset,
            "empty_form": formset.empty_form,
            "vorhandene_forms": vorhandene_forms,
            "selected_menu": "recycling_create",
        })
