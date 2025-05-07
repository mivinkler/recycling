from django.views.generic.edit import FormView
from django.shortcuts import redirect
from django.db import transaction
from django.urls import reverse_lazy

from warenwirtschaft.forms import RecyclingFormSet, UnloadForm
from warenwirtschaft.models import Recycling


class RecyclingCreateView(FormView):
    template_name = 'recycling/recycling_create.html'
    form_class = UnloadForm
    success_url = reverse_lazy('recycling_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form = kwargs.get('form') or self.get_form()

        if self.request.method == 'POST' and form.is_valid():
            unload = form.cleaned_data['unload']
            self.formset = RecyclingFormSet(self.request.POST, instance=unload, prefix='recycling')
        else:
            self.formset = RecyclingFormSet(prefix='recycling')

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
