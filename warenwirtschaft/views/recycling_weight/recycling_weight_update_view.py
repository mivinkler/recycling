from django.views import View
from django.shortcuts import render, redirect, get_object_or_404
from warenwirtschaft.models.recycling import Recycling

class RecyclingWeightUpdateView(View):
    template_name = 'recycling_weight/recycling_weight_update.html'

    def get(self, request, pk):
        # Kontext für die Anzeige des Formulars vorbereiten
        context = {
            "recycling_list": Recycling.objects.filter(status=1),
            "selected_menu": "recycling_weight_list",
            "edit_recycling": get_object_or_404(Recycling, pk=pk),
            "status_choices": Recycling.STATUS_CHOICES,
        }
        return render(request, self.template_name, context)

    def post(self, request, pk):
        # Recycling-Objekt abrufen
        recycling = get_object_or_404(Recycling, pk=pk)
        new_weight = request.POST.get('new_weight')
        new_status = request.POST.get('status')

        # Gewicht und Status aktualisieren
        if new_weight:
            recycling.weight = new_weight
        if new_status:
            recycling.status = new_status

        recycling.save()

        # Zurück zur Liste weiterleiten
        return redirect('recycling_weight_list')
