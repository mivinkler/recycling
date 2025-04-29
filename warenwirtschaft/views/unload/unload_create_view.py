from django.views.generic.edit import CreateView
from django.urls import reverse_lazy
from django.db import transaction
from warenwirtschaft.models import Unload, DeliveryUnit
from warenwirtschaft.forms import UnloadFormSet
from warenwirtschaft.forms import UnloadForm

class UnloadCreateView(CreateView):
    model = Unload
    template_name = 'unload/unload_create.html'
    form_class = UnloadForm
    context_object_name = 'unload'
    success_url = reverse_lazy('unload_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['formset'] = UnloadFormSet(self.request.POST)
        else:
            context['formset'] = UnloadFormSet()
        context['formset'].empty_form.prefix = 'unload-__prefix__'
        context['empty_form'] = context['formset'].empty_form
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        formset = context['formset']
        if formset.is_valid():
            with transaction.atomic():
                self.object = form.save()
                formset.instance = self.object
                formset.save()
            return super().form_valid(form)
        return self.render_to_response(self.get_context_data(form=form))
