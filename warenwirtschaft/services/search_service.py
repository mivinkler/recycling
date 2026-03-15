from django.core.exceptions import ValidationError
from django.db.models import Q
from django.utils.dateparse import parse_date

from warenwirtschaft.services.pagination_service import PaginationPreferenceMixin
from warenwirtschaft.services.sorting_service import SortingService


class SearchService:
    def __init__(self, request, search_fields=None, choices_fields=None, search_filters=None, field_configs=None):
        self.request = request
        self.field_configs = field_configs or []
        search_fields = search_fields or []
        self.search_fields = [field[0] if isinstance(field, tuple) else field for field in search_fields]
        self.choices_fields = choices_fields or {}
        self.search_filters = search_filters or []

        if self.field_configs:
            self.search_fields = self.get_sort_fields()
            if not self.search_filters:
                self.search_filters = self.build_search_filters()

    def get_sort_fields(self):
        if self.field_configs:
            return [config["field"] for config in self.field_configs]
        return list(self.search_fields)

    def get_active_fields(self):
        if self.field_configs:
            return [(config["field"], config["label"]) for config in self.field_configs]
        return [(field, field) for field in self.search_fields]

    def get_context_data(self):
        return {
            "request": self.request,
            "active_fields": self.get_active_fields(),
            "search_filters": self.search_filters,
            "has_active_filters": self.has_active_filters(),
            "search_query": self.request.GET.get("search", ""),
            "sort_param": self.request.GET.get("sort", ""),
        }

    def has_active_filters(self):
        if self.search_filters:
            for search_filter in self.search_filters:
                if search_filter["type"] == "date":
                    if search_filter.get("from_value") or search_filter.get("to_value"):
                        return True
                elif search_filter.get("value"):
                    return True
            return False

        return any(
            self.request.GET.get(param)
            for param in ("search", "date_start", "date_end", "status_filter")
        )

    def build_search_filters(self):
        search_filters = []

        for config in self.field_configs:
            search_filter = config.copy()
            field = search_filter["field"]
            filter_type = search_filter.get("type", "text")
            param = search_filter.get("param", field.replace("__", "_"))

            search_filter["type"] = filter_type
            search_filter["filter_field"] = search_filter.get("filter_field", field)

            if filter_type == "date":
                search_filter["from_param"] = f"{param}_from"
                search_filter["to_param"] = f"{param}_to"
                search_filter["from_value"] = self.request.GET.get(search_filter["from_param"], "").strip()
                search_filter["to_value"] = self.request.GET.get(search_filter["to_param"], "").strip()
            else:
                search_filter["param"] = param
                search_filter["value"] = self.request.GET.get(param, "").strip()

            if filter_type == "choice":
                search_filter["choices"] = [
                    {"value": str(value), "label": choice_label}
                    for value, choice_label in self._resolve_choices(search_filter.get("choices", []))
                ]
            else:
                search_filter["lookup"] = search_filter.get("lookup", "icontains")

            search_filters.append(search_filter)

        return search_filters

    def _resolve_choices(self, choices):
        if callable(choices):
            choices = choices()
        return list(choices)

    def apply_search(self, queryset):
        if self.search_filters:
            return self._apply_configured_filters(queryset)

        queryset = self._apply_text_search(queryset)
        queryset = self._apply_date_filter(queryset)
        queryset = self._apply_choice_filters(queryset)
        return queryset

    def _apply_configured_filters(self, queryset):
        for search_filter in self.search_filters:
            filter_type = search_filter.get("type", "text")
            field = search_filter.get("field")
            filter_field = search_filter.get("filter_field", field)

            if filter_type == "date":
                from_value = self.request.GET.get(search_filter["from_param"], "").strip()
                to_value = self.request.GET.get(search_filter["to_param"], "").strip()

                if from_value:
                    parsed_from = parse_date(from_value)
                    if parsed_from:
                        queryset = queryset.filter(**{f"{field}__date__gte": parsed_from})

                if to_value:
                    parsed_to = parse_date(to_value)
                    if parsed_to:
                        queryset = queryset.filter(**{f"{field}__date__lte": parsed_to})

                continue

            value = self.request.GET.get(search_filter["param"], "").strip()
            if not value:
                continue

            try:
                if filter_type == "choice":
                    queryset = queryset.filter(**{filter_field: value})
                else:
                    lookup = search_filter.get("lookup", "icontains")
                    queryset = queryset.filter(**{f"{filter_field}__{lookup}": value})
            except (TypeError, ValueError, ValidationError):
                continue

        return queryset

    def _apply_text_search(self, queryset):
        search_query = self.request.GET.get("search", "").strip().lower()
        if not search_query:
            return queryset

        q_objects = Q()

        for field, choices in self.choices_fields.items():
            label_to_value = {label.lower(): value for value, label in choices}
            if search_query in label_to_value:
                q_objects |= Q(**{field: label_to_value[search_query]})

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
        status_filter = self.request.GET.get("status_filter", "").strip().lower()
        choices = self.choices_fields.get("status")
        if choices and status_filter:
            label_to_value = {label.lower(): value for value, label in choices}
            if status_filter in label_to_value:
                queryset = queryset.filter(status=label_to_value[status_filter])

        return queryset


class SearchableListViewMixin(PaginationPreferenceMixin):
    field_configs = []
    search_distinct = False

    def get_field_configs(self):
        return self.field_configs

    def get_search_service(self):
        if not hasattr(self, "_search_service"):
            self._search_service = SearchService(self.request, field_configs=self.get_field_configs())
        return self._search_service

    def apply_search_and_sort(self, queryset):
        search_service = self.get_search_service()
        sorting_service = SortingService(self.request, search_service.get_sort_fields())

        queryset = search_service.apply_search(queryset)
        queryset = sorting_service.apply_sorting(queryset)

        if self.search_distinct:
            queryset = queryset.distinct()

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(self.get_search_service().get_context_data())
        return context
