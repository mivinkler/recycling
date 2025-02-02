from django.views.generic.edit import CreateView
from django.core.paginator import Paginator
from django.db.models import Q
from warenwirtschaft.models import Delivery, Device, Supplier
from warenwirtschaft.forms import DeliveryForm


class DeliveryCreateView(CreateView):
    model = Delivery
    template_name = "delivery/delivery_create.html"
    form_class = DeliveryForm
    paginate_by = 20

    # Поля, по которым будем искать
    search_fields = ["id", "avv_number", "name", "street", "postal_code", "city", "phone", "email", "note"]

    # Автоматическая генерация сортировки
    sort_mapping = {field: field for field in search_fields}
    sort_mapping.update({f"{key}_desc": f"-{val}" for key, val in sort_mapping.items()})

    def apply_search(self, queryset):
        """Поиск по всем полям из search_fields."""
        search_query = self.request.GET.get("search", "").strip()
        if not search_query:
            return queryset

        q_objects = Q()
        for field in self.search_fields:
            lookup = f"{field}__icontains"
            q_objects |= Q(**{lookup: search_query})

        return queryset.filter(q_objects)

    def apply_sorting(self, queryset):
        """Сортировка по переданному GET-параметру."""
        sort_field = self.sort_mapping.get(self.request.GET.get("sort"), "id")
        return queryset.order_by(sort_field)

    def get_queryset(self):
        """Фильтрация и сортировка списка доставок."""
        queryset = super().get_queryset()
        return self.apply_sorting(self.apply_search(queryset))

    def get_paginated_queryset(self, queryset):
        """Пагинация списка."""
        paginator = Paginator(queryset, self.paginate_by)
        page_number = self.request.GET.get("page", 1)
        return paginator.get_page(page_number)

    def get_context_data(self, **kwargs):
        """Добавляем в контекст список устройств и поставщиков."""
        context = super().get_context_data(**kwargs)
        context["devices"] = Device.objects.all()

        # Фильтрация и сортировка поставщиков
        suppliers_queryset = self.apply_sorting(self.apply_search(Supplier.objects.all()))
        context["page_obj"] = self.get_paginated_queryset(suppliers_queryset)

        # Передаём текущее значение поиска
        context["search_query"] = self.request.GET.get("search", "")

        return context
