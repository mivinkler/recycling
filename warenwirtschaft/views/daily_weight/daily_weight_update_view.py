from django.views.generic import TemplateView
from django.shortcuts import render, redirect, get_object_or_404
from warenwirtschaft.models import Unload, Recycling


class DailyWeightUpdateView(TemplateView):
    template_name = 'daily_weight/daily_weight_update.html'

    def get(self, request, model, pk):

        if model == "unload":
            edit_unload = get_object_or_404(Unload, pk=pk)
            edit_recycling = None
        else:
            edit_unload = None
            edit_recycling = get_object_or_404(Recycling, pk=pk)

        context = {
            "unload_list": Unload.objects.filter(status=1),
            "recycling_list": Recycling.objects.filter(status=1),

            "edit_unload": edit_unload,
            "edit_recycling": edit_recycling,

            "status_choices_unload": Unload.STATUS_CHOICES,
            "status_choices_recycling": Recycling.STATUS_CHOICES,

            "selected_menu": "daily_weight",
        }
        return render(request, self.template_name, context)


    def post(self, request, model, pk):

        if model == "unload":
            obj = get_object_or_404(Unload, pk=pk)
            new_status = request.POST.get("unload_status")
        else:
            obj = get_object_or_404(Recycling, pk=pk)
            new_status = request.POST.get("recycling_status")

        new_weight = request.POST.get("new_weight")
        new_note = request.POST.get("new_note")

        if new_weight:
            obj.weight = new_weight

        if new_status:
            obj.status = new_status

        if new_note is not None:
            obj.note = new_note

        obj.save()
        return redirect("daily_weight_list")
