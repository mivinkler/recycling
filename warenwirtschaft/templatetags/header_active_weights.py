from django import template
from django.db.models import Sum

from warenwirtschaft.models import DeliveryUnit, Unload, Recycling, DeviceCheck

register = template.Library()


@register.inclusion_tag("components/header_active_weights.html")
def header_active_weights():
    """
    Liefert die Gesamtgewichte aller aktiven Einheiten nach Bereichen
    zur Anzeige in der Kopfzeile.
    """

    # --- Anlieferung (DeliveryUnit) ---
    delivery_total = (
        DeliveryUnit.objects.filter(status=1)
        .aggregate(total=Sum("weight"))
        .get("total") or 0
    )

    # --- Vorsortierung (Unload) ---
    unload_total = (
        Unload.objects.filter(status=1)
        .aggregate(total=Sum("weight"))
        .get("total") or 0
    )

    # --- Aufbereitung (Recycling) ---
    recycling_total = (
        Recycling.objects.filter(status=1)
        .aggregate(total=Sum("weight"))
        .get("total") or 0
    )

    # --- Geräteprüfung (DeviceCheck) ---
    devicecheck_total = (
        DeviceCheck.objects.filter(status=1)
        .aggregate(total=Sum("weight"))
        .get("total") or 0
    )

    # --- Gesamtgewicht über alle Bereiche ---
    overall_total = (
        delivery_total + unload_total + recycling_total + devicecheck_total
    )

    return {
        "active_weight_delivery": delivery_total,
        "active_weight_unload": unload_total,
        "active_weight_recycling": recycling_total,
        "active_weight_devicecheck": devicecheck_total,
        "active_weight_total": overall_total,
    }
