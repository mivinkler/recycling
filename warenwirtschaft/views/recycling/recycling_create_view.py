from django.views import View
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.db import transaction

from warenwirtschaft.forms_neu.recycling_form import UnloadChoiceForm, RecyclingFormSet, RecyclingForm
from warenwirtschaft.models import Unload, Recycling


class RecyclingCreateView(View):
    template_name = "recycling/recycling_create.html"
    success_url = reverse_lazy("recycling_list")

    def get(self, request):
        form = UnloadChoiceForm()
        # ✨ префикс обязателен — ты сам генеришь имена полей в JS
        formset = RecyclingFormSet(queryset=Recycling.objects.none(), prefix="new")
        unload = None

        vorhandene_forms = [
            RecyclingForm(instance=obj, prefix=f"recycling_{obj.pk}")
            for obj in Recycling.objects.filter(status=1)
        ]

        return self.render_page(form, formset, vorhandene_forms, unload)

    def post(self, request):
        unload_form = UnloadChoiceForm(request.POST)
        formset = RecyclingFormSet(request.POST, queryset=Recycling.objects.none(), prefix="new")
        selected_ids = request.POST.getlist("selected_recycling")

        # 🇩🇪 Erst die Auswahl des Unload prüfen, dann bestehende Verknüpfungen setzen,
        # und NUR wenn neue Zeilen vorhanden sind, den FormSet validieren.
        if unload_form.is_valid():
            unload = unload_form.cleaned_data["unload"]

            # есть ли вообще строки в formset?
            has_new_rows = formset.total_form_count() > 0

            if has_new_rows and not formset.is_valid():
                # есть ошибки в новых строках — перерисовываем страницу с ошибками
                vorhandene_forms = [
                    RecyclingForm(instance=obj, prefix=f"recycling_{obj.pk}")
                    for obj in Recycling.objects.filter(status=1)
                ]
                return self.render_page(unload_form, formset, vorhandene_forms, unload)

            with transaction.atomic():
                # 1) Verknüpfungen für bestehende Recycling-Einträge
                for recycling in Recycling.objects.filter(status=1):
                    if str(recycling.pk) in selected_ids:
                        recycling.unloads.add(unload)
                    else:
                        recycling.unloads.remove(unload)

                # 2) Neue Recycling-Einträge aus dem FormSet speichern (falls vorhanden)
                if has_new_rows:
                    new_instances = formset.save(commit=False)
                    for instance in new_instances:
                        # 🇩🇪 Pflichtfelder setzen, weil sie nicht im Formular sind
                        instance.status = 1                 # z.B. „aktiv“ – поставь твой код статуса
                        instance.target = unload.target     # или фиксированное значение, например 2
                        instance.save()
                        instance.unloads.add(unload)

                # 2) Unload-Status updaten
                unload.status = 2
                unload.save()

            return redirect("recycling_update", pk=unload.pk)

        # Если Unload невалиден — просто перерисовать
        vorhandene_forms = [
            RecyclingForm(instance=obj, prefix=f"recycling_{obj.pk}")
            for obj in Recycling.objects.filter(status=1)
        ]
        unload = unload_form.cleaned_data.get("unload") if unload_form.is_valid() else None
        return self.render_page(unload_form, formset, vorhandene_forms, unload)

    def render_page(self, form, formset, vorhandene_forms, unload=None):
        return render(self.request, self.template_name, {
            "form": form,
            "formset": formset,
            "empty_form": formset.empty_form,
            "vorhandene_forms": vorhandene_forms,
            "unload": unload,
            "selected_menu": "recycling_create",
        })
