from django.db.models import Q

class SearchService:
    def __init__(self, request, search_fields):
        self.request = request
        self.search_fields = search_fields

    def apply_search(self, queryset):
        search_query = self.request.GET.get("search", "").strip()
        if not search_query:
            return queryset

        q_objects = Q()
        for field in self.search_fields:
            lookup = f"{field}__icontains"
            q_objects |= Q(**{lookup: search_query})

        return queryset.filter(q_objects)