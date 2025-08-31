from django.views.generic.edit import UpdateView
from django.urls import reverse_lazy
from warenwirtschaft.forms.customer_form import CustomerForm
from warenwirtschaft.models.customer import Customer

class CustomerUpdateView(UpdateView):
    model = Customer
    template_name = 'customer/customer_update.html'
    form_class = CustomerForm
    context_object_name = 'customer'
    success_url = reverse_lazy('customer_list')
