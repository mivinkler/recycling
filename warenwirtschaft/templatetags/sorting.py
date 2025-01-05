from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.simple_tag
def sort(name, field_name, current_sort):

    if current_sort == f"{field_name}_asc":
        asc_class = "active"
        desc_class = ""
    elif current_sort == f"{field_name}_desc":
        asc_class = ""
        desc_class = "active"
    else:
        asc_class = desc_class = ""

    html = f"""
        <div>
            <div>{name}</div>
            <div class="sort-icons">
                <a href="?sort={field_name}_asc" class="{asc_class}">▲</a>
                <a href="?sort={field_name}_desc" class="{desc_class}">▼</a>
            </div>
        </div>
    """
    return mark_safe(html)
