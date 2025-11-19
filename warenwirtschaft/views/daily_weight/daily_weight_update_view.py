from django.views.generic import TemplateView
from django.shortcuts import render, redirect, get_object_or_404
from warenwirtschaft.models.recycling import Recycling
from warenwirtschaft.models import Unload

class DailyWeightUpdateView(TemplateView):
    template_name = 'daily_weight/daily_weight_update.html'

    def get(self, request, pk):
        # Kontext für die Anzeige des Formulars vorbereiten
        context = {
            "recycling_list": Recycling.objects.filter(status=1),
            "unload_list": Unload.objects.filter(status=1),
            "edit_recycling": get_object_or_404(Recycling, pk=pk),
            "status_choices": Recycling.STATUS_CHOICES,
            "selected_menu": "daily_weight",
        }
        return render(request, self.template_name, context)

    def post(self, request, pk):
        # Recycling-Objekt abrufen
        recycling = get_object_or_404(Recycling, pk=pk)
        new_weight = request.POST.get('new_weight')
        new_status = request.POST.get('status')
        new_note = request.POST.get('note')

        # Gewicht und Status aktualisieren
        if new_weight:
            recycling.weight = new_weight
        if new_status:
            recycling.status = new_status
        if new_note:
            recycling.note = new_note

        recycling.save()

        # Zurück zur Liste weiterleiten
        return redirect('daily_weight_list')
