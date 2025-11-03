from django.views.generic import ListView
from warenwirtschaft.models import BarcodeGenerator
from warenwirtschaft.services.pagination_service import PaginationService

class BarcodeGeneratorListView(ListView):
    model = BarcodeGenerator
    template_name = 'barcode/barcode_generator_list.html'
    context_object_name = 'barcodes'
    paginate_by = 28

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        paginator = PaginationService(self.request, self.paginate_by)
        page_obj = paginator.get_paginated_queryset(self.get_queryset())
        context["page_obj"] = page_obj

        context['selected_menu'] = 'barcode_generator_list'
        context["dashboard"] = True
        return context
