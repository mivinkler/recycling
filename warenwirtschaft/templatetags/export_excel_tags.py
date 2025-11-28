from django import template

register = template.Library()

# Dieses Template-Tag liefert den Namen der Export-URL
# passend zum ausgewählten Menü zurück.

@register.simple_tag
def get_export_url_name(selected_menu: str) -> str | None:
    """
    Liefert den Namen der URL für den Excel-Export
    basierend auf dem ausgewählten Menü.
    """
    mapping = {
        "delivery_list": "delivery_export_excel",
        "unload_list": "unload_export_excel",
        "recycling_list": "recycling_export_excel",
        "shipping_list": "shipping_export_excel",
    }
    return mapping.get(selected_menu)
