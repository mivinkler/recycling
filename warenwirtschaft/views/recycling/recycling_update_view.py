from django.shortcuts import get_object_or_404, redirect, render
from django.views import View

from warenwirtschaft.forms.recycling_form import RecyclingForm
from warenwirtschaft.models.recycling import Recycling
from warenwirtschaft.recycling_page_mixin import RecyclingPageMixin


class RecyclingUpdateView(RecyclingPageMixin, View):
    def _get_recycling(self, recycling_pk):
        return get_object_or_404(Recycling, pk=recycling_pk)

    def _apply_new_weight(self, recycling, raw_weight):
        new_weight = (raw_weight or "").strip()
        if new_weight:
            # Leeres Feld soll das vorhandene Gewicht nicht ueberschreiben.
            recycling.weight = new_weight

    def get(self, request, recycling_pk):
        recycling = self._get_recycling(recycling_pk)
        form = RecyclingForm(instance=recycling)
        return render(
            request,
            self.template_name,
            self._build_context(edit_recycling=recycling, form=form),
        )

    def post(self, request, recycling_pk):
        recycling = self._get_recycling(recycling_pk)
        form = RecyclingForm(request.POST, instance=recycling)

        if form.is_valid():
            recycling = form.save(commit=False)
            self._apply_new_weight(recycling, request.POST.get("new_weight"))
            recycling.save()
            return redirect("recycling_create")

        return render(
            request,
            self.template_name,
            self._build_context(edit_recycling=recycling, form=form),
        )
