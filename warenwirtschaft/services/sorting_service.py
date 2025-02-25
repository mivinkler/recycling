class SortingService:
    def __init__(self, request, sort_fields):
        self.request = request
        self.sort_fields = {}

        for field in sort_fields:
            self.sort_fields[f"{field}_asc"] = field  # По возрастанию
            self.sort_fields[f"{field}_desc"] = f"-{field}"  # По убыванию

    def apply_sorting(self, queryset):
        sort_param = self.request.GET.get("sort", "id_asc")
        sort_field = self.sort_fields.get(sort_param, "id")

        return queryset.order_by(sort_field)
