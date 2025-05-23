from django.views.generic.edit import FormView
from django.shortcuts import redirect
from django.db import transaction
from django.urls import reverse_lazy

from warenwirtschaft.forms import UnloadFormSet, DeliveryUnitForm
from warenwirtschaft.models import Unload


class UnloadCreateView(FormView):
    template_name = 'unload/unload_create.html'
    form_class = DeliveryUnitForm
    success_url = reverse_lazy('unload_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form = kwargs.get('form') or self.get_form()

        if self.request.method == 'POST' and form.is_valid():
            delivery_unit = form.cleaned_data['delivery_unit']
            self.formset = UnloadFormSet(self.request.POST, instance=delivery_unit, prefix='unload')
        else:
            self.formset = UnloadFormSet(prefix='unload')

        context['formset'] = self.formset
        context['empty_form'] = self.formset.empty_form
        return context

    def form_valid(self, form):
        self.get_context_data(form=form)
        if self.formset.is_valid():
            with transaction.atomic():
                self.formset.save()
            return redirect(self.success_url)
        return self.form_invalid(form)
