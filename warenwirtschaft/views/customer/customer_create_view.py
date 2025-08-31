from django.views.generic.edit import CreateView
from django.urls import reverse_lazy
from warenwirtschaft.forms.customer_form import CustomerForm
from warenwirtschaft.models.customer import Customer

class CustomerCreateView(CreateView):
    model = Customer
    template_name = 'customer/customer_create.html'
    form_class = CustomerForm
    success_url = reverse_lazy('customer_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['selected_menu'] = 'customer_create'
        return context
