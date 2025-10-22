from django import template
from django.utils.safestring import mark_safe
from warenwirtschaft.services.barcode_image_service import BarcodeImageService

register = template.Library()

@register.filter(name="barcode_svg")  # {{ object.barcode|barcode_svg }}
def barcode_svg(code: str) -> str:
    if not code:
        return ""
    svg = BarcodeImageService(code).render_svg_str()
    return mark_safe(svg)

@register.simple_tag(name="barcode_svg_tag")  # {% barcode_svg_tag object.barcode %}
def barcode_svg_tag(code: str) -> str:
    if not code:
        return ""
    svg = BarcodeImageService(code).render_svg_str()
    return mark_safe(svg)
