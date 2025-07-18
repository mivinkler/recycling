from django.views.generic.edit import UpdateView
from django.urls import reverse
from warenwirtschaft.models import ReusableBarcode
from warenwirtschaft.forms import ReusableBarcodeForm

class ReusableBarcodeUpdateView(UpdateView):
    model = ReusableBarcode
    form_class = ReusableBarcodeForm
    template_name = 'barcode/reusable_barcode_update.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['selected_menu'] = 'reusable_barcode_update'
        return context

    def form_valid(self, form):
        self.object = form.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('reusable_barcode_detail', kwargs={'pk': self.object.pk})
