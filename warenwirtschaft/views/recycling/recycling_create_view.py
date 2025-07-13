from django.views import View
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.db import transaction

from warenwirtschaft.forms import UnloadForm, RecyclingFormSet, RecyclingForm
from warenwirtschaft.models import Unload, Recycling


class RecyclingCreateView(View):
    template_name = "recycling/recycling_create.html"
    success_url = reverse_lazy("recycling_list")

    def get(self, request):
        unload_form = UnloadForm()
        selected_unload = self.get_selected_unload(request)
        vorhandene_forms = self.build_vorhandene_forms(selected_unload)
        formset = RecyclingFormSet(queryset=Recycling.objects.none())

        return self.render_page(unload_form, formset, vorhandene_forms)

    def post(self, request):
        unload_form = UnloadForm(request.POST)
        formset = RecyclingFormSet(request.POST, queryset=Recycling.objects.none())
        selected_ids = request.POST.getlist("selected_recycling")
        unload = None

        vorhandene_recycling = Recycling.objects.filter(status=1)

        if unload_form.is_valid() and formset.is_valid():
            unload = unload_form.cleaned_data["unload"]

            with transaction.atomic():
                for recycling in vorhandene_recycling:
                    if str(recycling.pk) in selected_ids:
                        recycling.unloads.add(unload)
                    else:
                        recycling.unloads.remove(unload)

                instances = formset.save(commit=False)
                for instance in instances:
                    instance.save()
                    instance.unloads.add(unload)
                for obj in formset.deleted_objects:
                    obj.delete()

            return redirect(self.success_url)

        vorhandene_forms = self.build_vorhandene_forms(self.get_selected_unload(request))
        return self.render_page(unload_form, formset, vorhandene_forms)

    def get_selected_unload(self, request):
        selected_unload_id = request.GET.get("unload")
        if selected_unload_id:
            return Unload.objects.filter(id=selected_unload_id).first()
        return None

    def build_vorhandene_forms(self, selected_unload):
        forms = []
        for recycling in Recycling.objects.filter(status=1):
            form = RecyclingForm(instance=recycling, prefix=f"recycling_{recycling.pk}")
            if selected_unload and selected_unload in recycling.unloads.all():
                form.fields["selected"].initial = True
            forms.append(form)
        return forms

    def render_page(self, unload_form, formset, vorhandene_forms):
        return render(self.request, self.template_name, {
            "form": unload_form,
            "formset": formset,
            "vorhandene_forms": vorhandene_forms,
            "empty_form": formset.empty_form,
            "selected_menu": "recycling_create",
        })
