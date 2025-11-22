from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import FormView

from warenwirtschaft.models import Unload, Recycling
from warenwirtschaft.models.device_check import DeviceCheck
from warenwirtschaft.forms.device_check_form import DeviceCheckForm


class DeviceCheckCreateView(FormView):
    template_name = "device_check/device_check_create.html"
    form_class = DeviceCheckForm
    success_url = reverse_lazy("device_check_create")

    # GET: QuerySets in das Formular geben
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["unload_qs"] = Unload.objects.filter(status=5, deleted_at__isnull=True)
        kwargs["recycling_qs"] = Recycling.objects.filter(status=5, deleted_at__isnull=True)
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["unload_list"] = Unload.objects.filter(status=5, deleted_at__isnull=True)
        context["recycling_list"] = Recycling.objects.filter(status=5, deleted_at__isnull=True)
        context["selected_menu"] = "device_check_create"
        return context

    def form_valid(self, form):
        container_value = form.cleaned_data["container"]
        note = form.cleaned_data.get("note")
        new_weight = form.cleaned_data.get("weight")

        source_type_str, pk_str = container_value.split("-", 1)
        pk = int(pk_str)

        unload_obj = None
        recycling_obj = None

        if source_type_str == "unload":
            source_obj = get_object_or_404(Unload, pk=pk)
            unload_obj = source_obj
            source_type = 1
        else:
            source_obj = get_object_or_404(Recycling, pk=pk)
            recycling_obj = source_obj
            source_type = 2

        # Gewicht: wenn leer, dann das ursprüngliche Gewicht übernehmen
        weight = new_weight if new_weight is not None else source_obj.weight

        # DeviceCheck anlegen, Status immer 1 = Aktiv
        DeviceCheck.objects.create(
            source_type=source_type,
            unload=unload_obj,
            recycling=recycling_obj,
            box_type=source_obj.box_type,
            material=source_obj.material,
            weight=weight,
            status=1,
            note=note,
        )

        # Original-Eintrag auf 4 = Erledigt setzen
        source_obj.status = 4
        source_obj.save()

        return redirect(self.success_url)
