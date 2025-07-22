from django.views import View
from django.shortcuts import render, redirect, get_object_or_404
from warenwirtschaft.models.recycling import Recycling

class RecyclingWeightUpdateView(View):
    template_name = 'recycling_weight/recycling_weight_update.html'

    def get(self, request, pk):
        context = {
            "recycling_list": Recycling.objects.filter(status=1),
            "selected_menu": "recycling_weight_update",
            "edit_recycling": get_object_or_404(Recycling, pk=pk),
        }
        return render(request, self.template_name, context)  # ← исправлено
