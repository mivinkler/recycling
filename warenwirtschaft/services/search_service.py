from django.db.models import Q

class SearchService:
    def __init__(self, request, search_fields, choices_fields=None):
        self.request = request
        self.search_fields = [field[0] if isinstance(field, tuple) else field for field in search_fields]
        self.choices_fields = choices_fields or {}  # Пример: {"box_type": [(1, "Gitterbox"), ...]}

    def apply_search(self, queryset):
        search_query = self.request.GET.get("search", "").strip().lower()
        if not search_query:
            return queryset

        q_objects = Q()

        # Универсальная обработка choice-полей
        for field, choices in self.choices_fields.items():
            label_to_value = {label.lower(): value for value, label in choices}
            if search_query in label_to_value:
                q_objects |= Q(**{field: label_to_value[search_query]})

        # Обычные текстовые поля
        for field in self.search_fields:
            q_objects |= Q(**{f"{field}__icontains": search_query})

        return queryset.filter(q_objects)
