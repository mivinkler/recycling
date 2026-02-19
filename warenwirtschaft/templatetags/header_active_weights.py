from django import template
from django.db.models import Sum
from warenwirtschaft.models import Unload, Recycling

register = template.Library()

@register.inclusion_tag("components/header_active_weights.html")
def header_active_weights():
    def get_weight_by_status(model, status):
        return model.objects.filter(status=status).aggregate(total=Sum("weight")).get("total") or 0

    unload_aktiv = get_weight_by_status(Unload, 1)
    unload_bereit_fuer_behandlung = get_weight_by_status(Unload, 2)
    unload_bereit_fuer_abholung = get_weight_by_status(Unload, 3)
    unload_bereit_fuer_halle_2 = get_weight_by_status(Unload, 5)

    recycling_aktiv = get_weight_by_status(Recycling, 1)
    recycling_bereit_fuer_behandlung = get_weight_by_status(Recycling, 2)
    recycling_bereit_fuer_abholung = get_weight_by_status(Recycling, 3)
    recycling_bereit_fuer_halle_2 = get_weight_by_status(Recycling, 5)

    unload_total = unload_aktiv + unload_bereit_fuer_behandlung + unload_bereit_fuer_abholung + unload_bereit_fuer_halle_2
    recycling_total = recycling_aktiv + recycling_bereit_fuer_behandlung + recycling_bereit_fuer_abholung + recycling_bereit_fuer_halle_2

    overall_total = unload_total + recycling_total

    return {
        "unload_aktiv": unload_aktiv,
        "unload_bereit_fuer_behandlung": unload_bereit_fuer_behandlung,
        "unload_bereit_fuer_abholung": unload_bereit_fuer_abholung,
        "unload_bereit_fuer_halle_2": unload_bereit_fuer_halle_2,

        "recycling_aktiv": recycling_aktiv,
        "recycling_bereit_fuer_behandlung": recycling_bereit_fuer_behandlung,
        "recycling_bereit_fuer_abholung": recycling_bereit_fuer_abholung,
        "recycling_bereit_fuer_halle_2": recycling_bereit_fuer_halle_2,

        "unload_total": unload_total,
        "recycling_total": recycling_total,

        "active_weight_total": overall_total,
    }
