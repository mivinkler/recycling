from django.views.generic import DetailView
from django.core.paginator import Paginator
from warenwirtschaft.models import Delivery


from django.views.generic import DetailView
from django.core.paginator import Paginator
from warenwirtschaft.models import Delivery

class DeliveryDetailView(DetailView):
    model = Delivery
    template_name = "delivery/delivery_detail.html"
    context_object_name = "delivery"
    paginate_by = 14

    # Возможные параметры сортировки
    sort_mapping = {
        "id_asc": "id", "id_desc": "-id",
        "delivery_type_asc": "delivery_type", "delivery_type_desc": "-delivery_type",
        "device_asc": "device", "device_desc": "-device",
        "weight_asc": "weight", "weight_desc": "-weight",
        "status_asc": "status", "status_desc": "-status",
        "note_asc": "note", "note_desc": "-note",
    }

    def apply_sorting(self, queryset):
        """Применяем сортировку по параметру в GET-запросе"""
        sort_param = self.request.GET.get("sort", "id_asc")  # По умолчанию сортируем по id
        sort_field = self.sort_mapping.get(sort_param, "id")
        return queryset.order_by(sort_field), sort_param

    def get_paginated_queryset(self, queryset):
        """Разбиваем результаты на страницы"""
        paginator = Paginator(queryset, self.paginate_by)
        page_number = self.request.GET.get("page")
        return paginator.get_page(page_number)

    def get_context_data(self, **kwargs):
        """Добавляем в контекст отсортированные и разбитые на страницы объекты"""
        context = super().get_context_data(**kwargs)
        delivery = self.object  # Текущая поставка

        # Получаем все delivery_units, применяем сортировку
        delivery_units = delivery.deliveryunits.all()
        sorted_units, sort_param = self.apply_sorting(delivery_units)

        context["page_obj"] = self.get_paginated_queryset(sorted_units)
        context["sort_param"] = sort_param  # Передаем текущий параметр сортировки в шаблон
        return context

