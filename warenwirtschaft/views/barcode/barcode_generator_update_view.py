from django.views.generic.edit import UpdateView
from django.urls import reverse
from warenwirtschaft.models import BarcodeGenerator
from warenwirtschaft.forms.barcode_generator_form import BarcodeGeneratorForm

class BarcodeGeneratorUpdateView(UpdateView):
    model = BarcodeGenerator
    form_class = BarcodeGeneratorForm
    template_name = 'barcode/barcode_generator_update.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['selected_menu'] = 'barcode_generator_update'
        return context

    def form_valid(self, form):
        self.object = form.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('barcode_generator_detail', kwargs={'pk': self.object.pk})
