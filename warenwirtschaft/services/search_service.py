from django.db.models import Q
from django.utils.dateparse import parse_date


class SearchService:
    def __init__(self, request, search_fields, choices_fields=None):
        self.request = request
        self.search_fields = [field[0] if isinstance(field, tuple) else field for field in search_fields]
        self.choices_fields = choices_fields or {}

    def apply_search(self, queryset):
        queryset = self._apply_text_search(queryset)
        queryset = self._apply_date_filter(queryset)
        queryset = self._apply_choice_filters(queryset)
        return queryset

    def _apply_text_search(self, queryset):
        search_query = self.request.GET.get("search", "").strip().lower()
        if not search_query:
            return queryset

        q_objects = Q()

        # choice
       # Поиск по значению choice-полей
        for field, choices in self.choices_fields.items():
            label_to_value = {label.lower(): value for value, label in choices}
            if search_query in label_to_value:  # Возможно, стоит использовать точное совпадение
                q_objects |= Q(**{field: label_to_value[search_query]})


        # Textsuche
        for field in self.search_fields:
            q_objects |= Q(**{f"{field}__icontains": search_query})

        return queryset.filter(q_objects)

    def _apply_date_filter(self, queryset):
        date_start = self.request.GET.get("date_start")
        date_end = self.request.GET.get("date_end")

        if date_start:
            parsed_date_start = parse_date(date_start)
            if parsed_date_start:
                queryset = queryset.filter(created_at__date__gte=parsed_date_start)
        if date_end:
            parsed_date_end = parse_date(date_end)
            if parsed_date_end:
                queryset = queryset.filter(created_at__date__lte=parsed_date_end)

        return queryset

    def _apply_choice_filters(self, queryset):
        # Status
        status_filter = self.request.GET.get("status_filter", "").strip().lower()
        choices = self.choices_fields.get("status")
        if choices and status_filter:
            label_to_value = {label.lower(): value for value, label in choices}
            if status_filter in label_to_value:
                queryset = queryset.filter(status=label_to_value[status_filter])

        return queryset
