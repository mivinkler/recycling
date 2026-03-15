from django import template
from django.utils.html import format_html

register = template.Library()


@register.simple_tag(takes_context=True)
def sort_header(context, field_name, label):
    request = context["request"]
    current_sort = request.GET.get("sort", "")

    asc = f"{field_name}_asc"
    desc = f"{field_name}_desc"
    next_sort = asc if current_sort == desc else desc

    params = request.GET.copy()
    params["sort"] = next_sort
    params.pop("page", None)

    if current_sort == asc:
        arrow = format_html('<span class="table-header-arrow">&#9650;</span>')
    elif current_sort == desc:
        arrow = format_html('<span class="table-header-arrow">&#9660;</span>')
    else:
        arrow = ""

    active_class = " table-sort-link-active" if current_sort in {asc, desc} else ""

    return format_html(
        '<a href="?{}" class="table-sort-link{}">{}{}</a>',
        params.urlencode(),
        active_class,
        label,
        arrow,
    )
