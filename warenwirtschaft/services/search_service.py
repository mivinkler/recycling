from django.db.models import Q

class SearchService:
    def __init__(self, request, search_fields):
        self.request = request
        self.search_fields = [field[0] if isinstance(field, tuple) else field for field in search_fields]

    def apply_search(self, queryset):
        search_query = self.request.GET.get("search", "").strip()
        if not search_query:
            return queryset

        q_objects = Q()
        for field in self.search_fields:
            q_objects |= Q(**{f"{field}__icontains": search_query})

        return queryset.filter(q_objects)
