"""Simple search service for list views."""

from django.core.exceptions import ValidationError
from django.utils.dateparse import parse_date


class SearchService:
    def __init__(self, request, field_configs):
        self.request = request
        self.params = request.GET
        self.field_configs = field_configs or []
        self.search_filters = [self._build_filter(config) for config in self.field_configs]

    def _build_filter(self, config):
        search_filter = dict(config)
        search_filter["type"] = search_filter.get("type", "text")
        search_filter["filter_field"] = search_filter.get("filter_field", search_filter["field"])

        param = search_filter.get("param", search_filter["field"].replace("__", "_"))

        if search_filter["type"] == "date":
            search_filter["from_param"] = f"{param}_from"
            search_filter["to_param"] = f"{param}_to"
            search_filter["from_value"] = self._get_value(search_filter["from_param"])
            search_filter["to_value"] = self._get_value(search_filter["to_param"])
            return search_filter

        search_filter["param"] = param
        search_filter["value"] = self._get_value(param)

        if search_filter["type"] == "choice":
            choices = search_filter.get("choices", [])
            if callable(choices):
                choices = choices()
            search_filter["choices"] = [
                {"value": str(value), "label": label}
                for value, label in choices
            ]
            return search_filter

        search_filter["lookup"] = search_filter.get("lookup", "icontains")
        return search_filter

    def _get_value(self, name):
        return self.params.get(name, "").strip()

    def _has_value(self, search_filter):
        if search_filter["type"] == "date":
            return bool(search_filter.get("from_value") or search_filter.get("to_value"))
        return bool(search_filter.get("value"))

    def get_sort_fields(self):
        return [config["field"] for config in self.field_configs]

    def get_active_fields(self):
        return [(search_filter["field"], search_filter["label"]) for search_filter in self.search_filters]

    def get_context_data(self):
        return {
            "request": self.request,
            "active_fields": self.get_active_fields(),
            "search_filters": self.search_filters,
            "has_active_filters": any(self._has_value(search_filter) for search_filter in self.search_filters),
            "sort_param": self.params.get("sort", ""),
        }

    def apply_search(self, queryset):
        for search_filter in self.search_filters:
            if not self._has_value(search_filter):
                continue

            if search_filter["type"] == "date":
                queryset = self._apply_date_filter(queryset, search_filter)
                continue

            queryset = self._apply_value_filter(queryset, search_filter)

        return queryset

    def _apply_date_filter(self, queryset, search_filter):
        field = search_filter["field"]
        date_from = parse_date(search_filter.get("from_value"))
        date_to = parse_date(search_filter.get("to_value"))

        if date_from:
            queryset = queryset.filter(**{f"{field}__date__gte": date_from})
        if date_to:
            queryset = queryset.filter(**{f"{field}__date__lte": date_to})

        return queryset

    def _apply_value_filter(self, queryset, search_filter):
        field = search_filter["filter_field"]
        value = search_filter["value"]

        try:
            if search_filter["type"] == "choice":
                return queryset.filter(**{field: value})

            lookup = search_filter["lookup"]
            return queryset.filter(**{f"{field}__{lookup}": value})
        except (TypeError, ValueError, ValidationError):
            return queryset
