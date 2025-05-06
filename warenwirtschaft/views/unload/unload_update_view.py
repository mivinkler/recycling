from django.views.generic.edit import UpdateView
from django.db import transaction
from django.urls import reverse_lazy

from warenwirtschaft.models.delivery_unit import DeliveryUnit
from warenwirtschaft.forms import UnloadFormSet


class UnloadUpdateView(UpdateView):
    model = DeliveryUnit
    template_name = 'unload/delivery_unit_update.html'
    context_object_name = 'delivery_unit'
    fields = []
    success_url = reverse_lazy('unload_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        self.formset = UnloadFormSet(self.request.POST or None, instance=self.object, prefix='unload')
        context['formset'] = self.formset
        context['empty_form'] = self.formset.empty_form
        return context

    def form_valid(self, form):
        self.get_context_data()
        if self.formset.is_valid():
            with transaction.atomic():
                self.formset.save()
            return super().form_valid(form)
        return self.form_invalid(form)
