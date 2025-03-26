from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.simple_tag
def sort(name, field_name, current_sort):
    is_asc = current_sort == f"{field_name}_asc"
    is_desc = current_sort == f"{field_name}_desc"
    
    asc_class = "active" if is_asc else ""
    desc_class = "active" if is_desc else ""

    html = f"""
        <div class="title-sort">
            <div>{name}</div>
            <div class="sort-icons">
                <a href="?sort={field_name}_asc" class="{asc_class}">△</a>
                <a href="?sort={field_name}_desc" class="{desc_class}">▽</a>
            <div>
        </div>
    """
    return mark_safe(html)
