from django.core.paginator import Paginator


class PaginationService:
    PAGE_SIZE_PARAM = "per_page"
    COOKIE_NAME = "per_page"
    MIN_PAGE_SIZE = 5
    MAX_PAGE_SIZE = 100

    def __init__(
        self,
        request,
        paginate_by,
        page_size_param=None,
        cookie_name=None,
        min_page_size=None,
        max_page_size=None,
    ):
        self.request = request
        self.page_size_param = page_size_param or self.PAGE_SIZE_PARAM
        self.cookie_name = cookie_name or self.COOKIE_NAME
        self.min_page_size = min_page_size or self.MIN_PAGE_SIZE
        self.max_page_size = max_page_size or self.MAX_PAGE_SIZE
        self.paginate_by = self.resolve_paginate_by(
            request,
            paginate_by,
            page_size_param=self.page_size_param,
            cookie_name=self.cookie_name,
            min_page_size=self.min_page_size,
            max_page_size=self.max_page_size,
        )

    @classmethod
    def parse_page_size(cls, value, min_page_size, max_page_size):
        try:
            page_size = int(value)
        except (TypeError, ValueError):
            return None

        return max(min_page_size, min(max_page_size, page_size))

    @classmethod
    def resolve_paginate_by(
        cls,
        request,
        default_paginate_by,
        page_size_param=None,
        cookie_name=None,
        min_page_size=None,
        max_page_size=None,
    ):
        if default_paginate_by is None:
            return None

        page_size_param = page_size_param or cls.PAGE_SIZE_PARAM
        cookie_name = cookie_name or cls.COOKIE_NAME
        min_page_size = min_page_size or cls.MIN_PAGE_SIZE
        max_page_size = max_page_size or cls.MAX_PAGE_SIZE

        page_size = cls.parse_page_size(request.GET.get(page_size_param, ""), min_page_size, max_page_size)
        if page_size is not None:
            return page_size

        page_size = cls.parse_page_size(request.COOKIES.get(cookie_name, ""), min_page_size, max_page_size)
        if page_size is not None:
            return page_size

        return default_paginate_by

    def get_paginated_queryset(self, queryset):
        """ Falls kein ORDER BY vorhanden ist: stabile Sortierung erzwingen.
            
            TODO: ordering in model: 
                class Meta:
                    ordering = ["created_at"] """
        
        if hasattr(queryset, "ordered") and not queryset.ordered:
            queryset = queryset.order_by("created_at")

        paginator = Paginator(queryset, self.paginate_by)
        page_number = self.request.GET.get("page", 1)
        return paginator.get_page(page_number)


class PaginationPreferenceMixin:
    page_size_param = PaginationService.PAGE_SIZE_PARAM
    page_size_cookie_name = PaginationService.COOKIE_NAME
    min_page_size = PaginationService.MIN_PAGE_SIZE
    max_page_size = PaginationService.MAX_PAGE_SIZE
    page_size_options = (10, 20, 30, 50)

    def get_current_page_size(self, default_paginate_by=None):
        if default_paginate_by is None:
            default_paginate_by = getattr(self, "paginate_by", None)

        return PaginationService.resolve_paginate_by(
            self.request,
            default_paginate_by,
            page_size_param=self.page_size_param,
            cookie_name=self.page_size_cookie_name,
            min_page_size=self.min_page_size,
            max_page_size=self.max_page_size,
        )

    def get_paginate_by(self, queryset):
        default_paginate_by = super().get_paginate_by(queryset)

        if default_paginate_by is None:
            return None

        return self.get_current_page_size(default_paginate_by)

    def get_page_size_context(self, current_page_size=None):
        if current_page_size is None:
            current_page_size = self.get_current_page_size()

        page_size_options = sorted({*self.page_size_options, current_page_size})

        return {
            "current_page_size": current_page_size,
            "page_size_param": self.page_size_param,
            "page_size_min": self.min_page_size,
            "page_size_max": self.max_page_size,
            "page_size_options": page_size_options,
        }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        page_obj = context.get("page_obj")
        current_page_size = page_obj.paginator.per_page if page_obj else self.get_current_page_size()
        context.update(self.get_page_size_context(current_page_size))
        return context

    def render_to_response(self, context, **response_kwargs):
        response = super().render_to_response(context, **response_kwargs)
        current_page_size = context.get("current_page_size")

        if current_page_size:
            response.set_cookie(
                self.page_size_cookie_name,
                str(current_page_size),
                max_age=60 * 60 * 24 * 365,
                samesite="Lax",
            )

        return response
