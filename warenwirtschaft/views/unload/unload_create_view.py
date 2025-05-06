from django.views.generic.edit import FormView
from django.shortcuts import redirect
from django.db import transaction
from warenwirtschaft.forms import UnloadFormSet
from warenwirtschaft.models import Unload

class UnloadCreateView(FormView):
    template_name = 'unload/unload_create.html'
    success_url = '/warenwirtschaft/unload/list/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['formset'] = UnloadFormSet(self.request.POST or None, prefix='unload')
        context['empty_form'] = context['formset'].empty_form
        return context

    def form_valid(self, form):
        formset = UnloadFormSet(self.request.POST, prefix='unload')
        delivery_unit = form.cleaned_data['delivery_unit']

        with transaction.atomic():
            for f in formset.cleaned_data:
                if not f.get('DELETE'):
                    Unload.objects.create(
                        delivery_unit=delivery_unit,
                        **{k: v for k, v in f.items() if k not in ['DELETE', 'delivery_unit']}
                    )

        return redirect(self.success_url)
