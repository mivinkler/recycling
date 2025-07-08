from django.views import View
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.db import transaction

from warenwirtschaft.models import Unload, Recycling
from warenwirtschaft.forms import UnloadForm, RecyclingFormSet, RecyclingForm


class RecyclingUpdateView(View):
    template_name = "recycling/recycling_update.html"
    success_url = reverse_lazy("recycling_list")

    def get(self, request, pk):
        unload = get_object_or_404(Unload, pk=pk)
        form_unload = UnloadForm(initial={"unload": unload})
        formset = RecyclingFormSet(queryset=Recycling.objects.none())  # Neue Wagen
        vorhandene_forms = self.build_vorhandene_forms(unload)
        return self.render_page(form_unload, formset, vorhandene_forms)

    def post(self, request, pk):
        unload = get_object_or_404(Unload, pk=pk)
        form_unload = UnloadForm(request.POST)
        formset = RecyclingFormSet(request.POST)
        selected_ids = request.POST.getlist("selected_recycling")

        # leere Zeilen erlauben
        for form in formset.forms:
            if not form.has_changed():
                form.empty_permitted = True

        # Wir ignorieren unload aus dem Formular — immer verwenden wir URL-unload (pk)
        if formset.is_valid():
            with transaction.atomic():
                self.update_recycling_links(unload, selected_ids)
                self.save_new_recycling(formset, unload)
            return redirect(self.success_url)

        # Fehlerfall
        vorhandene_forms = self.build_vorhandene_forms(unload)
        return self.render_page(form_unload, formset, vorhandene_forms)

    def update_recycling_links(self, unload, selected_ids):
        """Verknüpfe oder entferne Recycling-Einträge basierend auf Checkbox-Auswahl."""
        selected_ids = set(map(str, selected_ids))

        for recycling in Recycling.objects.filter(status=1):
            linked = unload in recycling.unloads.all()
            selected = str(recycling.pk) in selected_ids

            if selected and not linked:
                recycling.unloads.add(unload)
            elif not selected and linked:
                recycling.unloads.remove(unload)

    def save_new_recycling(self, formset, unload):
        for instance in formset.save(commit=False):
            instance.save()
            instance.unloads.add(unload)

        for obj in formset.deleted_objects:
            obj.delete()

    def build_vorhandene_forms(self, unload):
        """Alle aktiven Recycling, Checkbox gesetzt wenn mit Unload verknüpft."""
        forms = []
        for recycling in Recycling.objects.filter(status=1):
            form = RecyclingForm(instance=recycling, prefix=f"recycling_{recycling.pk}")
            if unload in recycling.unloads.all():
                form.fields["selected"].initial = True
            forms.append(form)
        return forms

    def render_page(self, form_unload, formset, vorhandene_forms):
        return render(self.request, self.template_name, {
            "form": form_unload,
            "formset": formset,
            "vorhandene_forms": vorhandene_forms,
            "empty_form": formset.empty_form,
            "unload": form_unload.initial["unload"],
        })
