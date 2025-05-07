from django.views.generic.edit import UpdateView
from django.db import transaction
from django.urls import reverse_lazy

from warenwirtschaft.models.unload import Unload
from warenwirtschaft.forms import RecyclingFormSet


class RecyclingUpdateView(UpdateView):
    model = Unload
    template_name = 'recycling/recycling_update.html'
    context_object_name = 'unload'
    fields = []
    success_url = reverse_lazy('recycling_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.method == 'POST':
            self.formset = RecyclingFormSet(self.request.POST, instance=self.object, prefix='recycling')
        else:
            self.formset = RecyclingFormSet(instance=self.object, prefix='recycling')
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
