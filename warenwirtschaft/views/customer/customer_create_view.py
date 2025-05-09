from django.views.generic.edit import CreateView
from warenwirtschaft.models.customer import Customer
from warenwirtschaft.forms import CustomerForm
from django.urls import reverse_lazy

class CustomerCreateView(CreateView):
    model = Customer
    template_name = 'customer/customer_create.html'
    form_class = CustomerForm
    success_url = reverse_lazy('customer_list')
