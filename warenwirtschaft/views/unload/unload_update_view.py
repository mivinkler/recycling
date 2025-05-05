from django.views.generic.edit import FormView
from django.shortcuts import get_object_or_404, redirect
from warenwirtschaft.models import DeliveryUnit
from warenwirtschaft.forms import UnloadDeliveryUnitForm, UnloadFormSet
from django.db import transaction
from warenwirtschaft.models.unload import Unload

class UnloadUpdateView(FormView):
    form_class = UnloadDeliveryUnitForm
    template_name = 'unload/unload_update.html'
    success_url = '/warenwirtschaft/unload/list/'

    def get_delivery_unit(self):
        pk = self.kwargs['pk']
        unload = get_object_or_404(Unload, pk=pk)
        return unload.delivery_unit  # wichtig: delivery_unit über unload erhalten

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        delivery_unit = self.get_delivery_unit()
        formset = UnloadFormSet(self.request.POST or None, instance=delivery_unit, prefix='unload')
        context.update({
            'formset': formset,
            'empty_form': formset.empty_form,
            'delivery_unit': delivery_unit,
        })
        return context

    def form_valid(self, form):
        delivery_unit = self.get_delivery_unit()
        formset = UnloadFormSet(self.request.POST, instance=delivery_unit, prefix='unload')
        if formset.is_valid():
            with transaction.atomic():
                formset.save()
            return redirect(self.success_url)
        return self.render_to_response(self.get_context_data())