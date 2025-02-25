from django.core.paginator import Paginator

class PaginationService:
    def __init__(self, request, paginate_by):
        self.request = request
        self.paginate_by = paginate_by

    def get_paginated_queryset(self, queryset):
        paginator = Paginator(queryset, self.paginate_by)
        page_number = self.request.GET.get("page", 1)
        return paginator.get_page(page_number)
