from django.views.generic.edit import CreateView
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from warenwirtschaft.models import Delivery, Material, DeliveryUnit
from warenwirtschaft.forms import DeliveryForm
from warenwirtschaft.services.search_service import SearchService
from warenwirtschaft.services.sorting_service import SortingService
from warenwirtschaft.services.pagination_service import PaginationService

class DeliveryCreateView(CreateView):
    model = Delivery
    template_name = "delivery/delivery_create.html"
    form_class = DeliveryForm
    paginate_by = 20
    success_url = reverse_lazy('delivery_list')

    active_fields = [
        ("supplier__id", "ID"),
        ("supplier__avv_number", "AVV-Nummer"),
        ("supplier__name", "Name"),
        ("supplier__street", "Straße"),
        ("supplier__postal_code", "PLZ"),
        ("supplier__city", "Stadt"),
        ("supplier__phone", "Telefon"),
        ("supplier__email", "Email"),
        ("supplier__note", "Anmerkung"),
    ]

    def get_queryset(self):
        queryset = super().get_queryset()

        fields = [field[0] for field in self.active_fields]  # Wir nehmen nur die Schlüssel

        queryset = SearchService(self.request, fields).apply_search(queryset)
        queryset = SortingService(self.request, fields).apply_sorting(queryset)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        paginator = PaginationService(self.request, self.paginate_by)
        page_obj = paginator.get_paginated_queryset(self.get_queryset())

        context["page_obj"] = page_obj
        context["materials"] = Material.objects.all()
        context["search_query"] = self.request.GET.get("search", "")
        context["active_fields"] = self.active_fields

        return context

    def post(self, request, *args, **kwargs):
        form = self.get_form()

        # Delivery
        delivery = form.save()

        # DeliveryUnit
        index = 0
        while f"form-{index}-material" in request.POST:
            delivery_type = request.POST.get(f"form-{index}-delivery_type")
            material_id = request.POST.get(f"form-{index}-material")
            weight = request.POST.get(f"form-{index}-weight", 0)

            DeliveryUnit.objects.create(
                delivery=delivery,
                delivery_type=delivery_type,
                material_id=material_id,
                weight=weight
            )
            index += 1

        return HttpResponseRedirect(self.success_url)