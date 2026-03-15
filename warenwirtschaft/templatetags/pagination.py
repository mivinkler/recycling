from django import template

register = template.Library()


@register.inclusion_tag("components/pagination.html", takes_context=True)
def paginate(context, page_obj):
    request = context.get("request")
    query_params = request.GET.copy() if request else None
    page_size_param = context.get("page_size_param", "per_page")

    def page_link(page_number):
        if query_params is None:
            return f"?page={page_number}"
        params = query_params.copy()
        params["page"] = page_number
        return f"?{params.urlencode()}"

    page_links = []

    if page_obj.has_previous():
        page_links.append({"type": "link", "href": page_link(page_obj.previous_page_number()), "label": "\u00ab"})
    else:
        page_links.append({"type": "span", "label": "\u00ab"})

    if page_obj.number > 3:
        page_links.append({"type": "link", "href": page_link(1), "label": "1"})
        if page_obj.number > 4:
            page_links.append({"type": "span", "label": "..."})

    for num in range(max(1, page_obj.number - 2), min(page_obj.paginator.num_pages + 1, page_obj.number + 3)):
        if num == page_obj.number:
            page_links.append({"type": "current", "label": str(num)})
        else:
            page_links.append({"type": "link", "href": page_link(num), "label": str(num)})

    if page_obj.number < page_obj.paginator.num_pages - 2:
        if page_obj.number < page_obj.paginator.num_pages - 3:
            page_links.append({"type": "span", "label": "..."})
        page_links.append({
            "type": "link",
            "href": page_link(page_obj.paginator.num_pages),
            "label": str(page_obj.paginator.num_pages),
        })

    if page_obj.has_next():
        page_links.append({"type": "link", "href": page_link(page_obj.next_page_number()), "label": "\u00bb"})
    else:
        page_links.append({"type": "span", "label": "\u00bb"})

    hidden_params = []
    if query_params is not None:
        hidden_params = [
            {"key": key, "value": value}
            for key, value in query_params.items()
            if key not in {"page", page_size_param}
        ]

    return {
        "page_obj": page_obj,
        "page_links": page_links,
        "has_multiple_pages": page_obj.paginator.num_pages > 1,
        "hidden_params": hidden_params,
        "current_page_size": context.get("current_page_size", page_obj.paginator.per_page),
        "page_size_param": page_size_param,
        "page_size_min": context.get("page_size_min", 5),
        "page_size_max": context.get("page_size_max", 100),
    }
