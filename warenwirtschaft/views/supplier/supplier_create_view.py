from django.views.generic.edit import CreateView
from django.urls import reverse_lazy
from warenwirtschaft.forms import SupplierForm
from warenwirtschaft.models.supplier import Supplier

class SupplierCreateView(CreateView):
    model = Supplier
    template_name = 'supplier/supplier_create.html'
    form_class = SupplierForm
    success_url = reverse_lazy('supplier_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['selected_menu'] = 'supplier_create'
        return context
