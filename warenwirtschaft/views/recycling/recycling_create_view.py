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
        form = UnloadChoiceForm()
        formset = RecyclingFormSet(queryset=Recycling.objects.none())
        unload = None

        vorhandene_forms = [
            RecyclingForm(instance=obj, prefix=f"recycling_{obj.pk}")
            for obj in Recycling.objects.filter(status=1)
        ]

        return self.render_page(form, formset, vorhandene_forms, unload)

    def post(self, request):
        unload_form = UnloadChoiceForm(request.POST)
        formset = RecyclingFormSet(request.POST, queryset=Recycling.objects.none())
        selected_ids = request.POST.getlist("selected_recycling")

        if unload_form.is_valid() and formset.is_valid():
            unload = unload_form.cleaned_data["unload"]

            with transaction.atomic():
                for recycling in Recycling.objects.filter(status=1):
                    if str(recycling.pk) in selected_ids:
                        recycling.unloads.add(unload)
                    else:
                        recycling.unloads.remove(unload)

                new_instances = formset.save(commit=False)
                for instance in new_instances:
                    instance.save()
                    instance.unloads.add(unload)

                for deleted in formset.deleted_objects:
                    deleted.delete()

                unload.status = 2
                unload.save()

            return redirect("recycling_update", pk=unload.pk)

        vorhandene_forms = [
            RecyclingForm(instance=obj, prefix=f"recycling_{obj.pk}")
            for obj in Recycling.objects.filter(status=1)
        ]
        unload = unload_form.cleaned_data.get("unload") if unload_form.is_valid() else None
        return self.render_page(unload_form, formset, vorhandene_forms, unload)

        print("Unload object:", unload)
        print("Unload PK:", unload.pk)

    def render_page(self, form, formset, vorhandene_forms, unload=None):
        return render(self.request, self.template_name, {
            "form": form,
            "formset": formset,
            "empty_form": formset.empty_form,
            "vorhandene_forms": vorhandene_forms,
            "unload": unload,
            "selected_menu": "recycling_create",
        })
