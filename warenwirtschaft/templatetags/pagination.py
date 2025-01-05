from django import template
from django.utils.safestring import mark_safe  # Zum Markieren des Strings als sicher

register = template.Library()

@register.simple_tag
def paginate(page_obj):
    if page_obj.paginator.num_pages <= 1:
        return ''  # Wenn es weniger als zwei Seiten gibt, nichts zurückgeben

    pagination = []

    # "Zurück"-Schaltfläche
    if page_obj.has_previous():
        pagination.append(f'<a href="?page={page_obj.previous_page_number()}">&laquo;</a>')

    # Erste Seite und "..."
    if page_obj.number > 3:
        pagination.append(f'<a href="?page=1">1</a>')
        if page_obj.number > 4:
            pagination.append('<span>...</span>')

    # Aktuelle Seite und benachbarte Seiten
    for num in range(max(1, page_obj.number - 2), min(page_obj.paginator.num_pages + 1, page_obj.number + 3)):
        if num == page_obj.number:
            pagination.append(f'<span class="current">{num}</span>')
        else:
            pagination.append(f'<a href="?page={num}">{num}</a>')

    # "..." und letzte Seite
    if page_obj.number < page_obj.paginator.num_pages - 2:
        if page_obj.number < page_obj.paginator.num_pages - 3:
            pagination.append('<span>...</span>')
        pagination.append(f'<a href="?page={page_obj.paginator.num_pages}">{page_obj.paginator.num_pages}</a>')

    # "Weiter"-Schaltfläche
    if page_obj.has_next():
        pagination.append(f'<a href="?page={page_obj.next_page_number()}">&raquo;</a>')

    # Markiere HTML als sicher
    return mark_safe(f'<div class="pagination">{" ".join(pagination)}</div>')
