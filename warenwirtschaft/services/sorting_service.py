class SortingService:
    def __init__(self, request, sort_fields):
        self.request = request
        self.sort_fields = {}

        for field in sort_fields:
            self.sort_fields[f"{field}_asc"] = field
            self.sort_fields[f"{field}_desc"] = f"-{field}"

    def apply_sorting(self, queryset):
        sort_param = self.request.GET.get("sort", "").strip()
        sort_field = self.sort_fields.get(sort_param)

        if sort_field:
            return queryset.order_by(sort_field)
        
        # Wenn keine Sortierung angegeben ist, geben Sie die Standardsortierung zurück
        return queryset.order_by("-created_at")
