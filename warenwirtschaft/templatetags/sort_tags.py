from django import template
from django.utils.html import format_html

register = template.Library()

@register.simple_tag(takes_context=True)
def sort_header(context, field_name, label):
    request = context['request']
    current_sort = request.GET.get('sort', '')

    asc = f"{field_name}_asc"
    desc = f"{field_name}_desc"

    if current_sort == asc:
        arrow = '<span class="table-head-arrow">▼</span>'
    elif current_sort == desc:
        arrow = '<span class="table-head-arrow">▲</span>'
    else:
        arrow = ''

    return format_html('{} {}', label, format_html(arrow))
