class QuerysetSorter:
    def __init__(self, request, sort_fields):
        self.request = request
        self.sort_fields = {field: field for field in sort_fields}
        self.sort_fields.update({f"{key}_desc": f"-{val}" for key, val in self.sort_fields.items()})

    def apply_sorting(self, queryset):
        sort_param = self.request.GET.get("sort", "id_asc")
        sort_field = self.sort_fields.get(sort_param, "id")

        return queryset.order_by(sort_field)
