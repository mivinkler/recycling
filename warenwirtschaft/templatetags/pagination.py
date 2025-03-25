from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.simple_tag
def paginate(page_obj):
    # Wenn es nur eine Seite gibt, zeigen wir keine Paginierung an
    if page_obj.paginator.num_pages <= 1:
        return ''

    pagination = []

    # "Zurück"-Button
    if page_obj.has_previous():
        pagination.append(f'<a href="?page={page_obj.previous_page_number()}">&laquo;</a>')
    else:
        pagination.append('<span>&laquo;</span>')  # Deaktiviert, wenn keine vorherige Seite existiert

    # Erste Seite und "..."
    if page_obj.number > 3:
        pagination.append(f'<a href="?page=1">1</a>')  # Erster Seitenlink
        if page_obj.number > 4:
            pagination.append('<span>...</span>')  # "..." wenn mehr als 4 Seiten davor sind

    # Aktuelle Seite und die angrenzenden Seiten anzeigen
    for num in range(max(1, page_obj.number - 2), min(page_obj.paginator.num_pages + 1, page_obj.number + 3)):
        if num == page_obj.number:
            pagination.append(f'<span class="current">{num}</span>')  # Markiert die aktuelle Seite
        else:
            pagination.append(f'<a href="?page={num}">{num}</a>')

    # "..." und letzte Seite anzeigen, falls nötig
    if page_obj.number < page_obj.paginator.num_pages - 2:
        if page_obj.number < page_obj.paginator.num_pages - 3:
            pagination.append('<span>...</span>')  # "..." wenn mehr als 4 Seiten danach sind
        pagination.append(f'<a href="?page={page_obj.paginator.num_pages}">{page_obj.paginator.num_pages}</a>')

    # "Weiter"-Button
    if page_obj.has_next():
        pagination.append(f'<a href="?page={page_obj.next_page_number()}">&raquo;</a>')
    else:
        pagination.append('<span>&raquo;</span>')  # Deaktiviert, wenn keine nächste Seite existiert

    return mark_safe(f'<div class="pagination">{" ".join(pagination)}</div>')
