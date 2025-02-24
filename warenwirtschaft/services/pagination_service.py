from django.core.paginator import Paginator

class QuerysetPaginator:
    def __init__(self, request, per_page):
        self.request = request
        self.per_page = per_page

    def paginate(self, queryset):
        paginator = Paginator(queryset, self.per_page)
        page_number = self.request.GET.get("page", 1)
        return paginator.get_page(page_number)