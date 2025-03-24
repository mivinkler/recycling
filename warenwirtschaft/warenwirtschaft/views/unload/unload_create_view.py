from django.views.generic.edit import CreateView
from warenwirtschaft.forms import UnloadForm
from warenwirtschaft.models.material import Material
from warenwirtschaft.models.unload import Unload
from warenwirtschaft.models.delivery_unit import DeliveryUnit
from warenwirtschaft.services.search_service import SearchService
from warenwirtschaft.services.sorting_service import SortingService
from warenwirtschaft.services.pagination_service import PaginationService


class UnloadCreateView(CreateView):
    model = Unload
    template_name = "unload/unload_create.html"
    form_class = UnloadForm
    paginate_by = 6

    def get_queryset(self):
        queryset = super().get_queryset()

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        paginator = PaginationService(self.request, self.paginate_by)

        context["delivery_units"] = paginator.get_paginated_queryset(DeliveryUnit.objects.all())
        context["materials"] = Material.objects.only("id", "name")

        return context