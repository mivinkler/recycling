"""Simple mixin for searchable and sortable list views."""

from warenwirtschaft.services.pagination_service import PaginationPreferenceMixin
from warenwirtschaft.services.search_service import SearchService
from warenwirtschaft.services.sorting_service import SortingService


class ListViewService(PaginationPreferenceMixin):
    field_configs = []
    search_distinct = False

    def get_field_configs(self):
        return self.field_configs

    def get_search_service(self):
        if not hasattr(self, "_search_service"):
            self._search_service = SearchService(self.request, self.get_field_configs())
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
