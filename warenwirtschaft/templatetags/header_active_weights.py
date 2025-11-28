from django import template
from django.db.models import Sum
from warenwirtschaft.models import Unload, Recycling, DeviceCheck

register = template.Library()

@register.inclusion_tag("components/header_active_weights.html")
def header_active_weights():
    """
    Liefert die Gesamtgewichte aller aktiven Einheiten nach Bereichen
    zur Anzeige in der Kopfzeile.
    """

    def get_weight_by_status(model, status):
        """
        Die Funktion gibt 0 zurück, wenn keine Daten vorhanden sind.
        """
        return model.objects.filter(status=status).aggregate(total=Sum("weight")).get("total") or 0

    # Вес по статусам для каждого раздела
    unload_aktiv = get_weight_by_status(Unload, 1)
    unload_bereit_fuer_behandlung = get_weight_by_status(Unload, 2)
    unload_bereit_fuer_abholung = get_weight_by_status(Unload, 3)
    unload_bereit_fuer_halle_2 = get_weight_by_status(Unload, 5)

    recycling_aktiv = get_weight_by_status(Recycling, 1)
    recycling_bereit_fuer_behandlung = get_weight_by_status(Recycling, 2)
    recycling_bereit_fuer_abholung = get_weight_by_status(Recycling, 3)
    recycling_bereit_fuer_halle_2 = get_weight_by_status(Recycling, 5)

    devicecheck_aktiv = get_weight_by_status(DeviceCheck, 1)
    devicecheck_bereit_fuer_behandlung = get_weight_by_status(DeviceCheck, 2)
    devicecheck_bereit_fuer_abholung = get_weight_by_status(DeviceCheck, 3)
    devicecheck_bereit_fuer_halle_2 = get_weight_by_status(DeviceCheck, 5)

    # Суммируем веса по статусам для каждого раздела
    unload_total = unload_aktiv + unload_bereit_fuer_behandlung + unload_bereit_fuer_abholung + unload_bereit_fuer_halle_2
    recycling_total = recycling_aktiv + recycling_bereit_fuer_behandlung + recycling_bereit_fuer_abholung + recycling_bereit_fuer_halle_2
    devicecheck_total = devicecheck_aktiv + devicecheck_bereit_fuer_behandlung + devicecheck_bereit_fuer_abholung + devicecheck_bereit_fuer_halle_2

    # Общий итог по всем разделам
    overall_total = unload_total + recycling_total + devicecheck_total

    return {
        "unload_aktiv": unload_aktiv,
        "unload_bereit_fuer_behandlung": unload_bereit_fuer_behandlung,
        "unload_bereit_fuer_abholung": unload_bereit_fuer_abholung,
        "unload_bereit_fuer_halle_2": unload_bereit_fuer_halle_2,

        "recycling_aktiv": recycling_aktiv,
        "recycling_bereit_fuer_behandlung": recycling_bereit_fuer_behandlung,
        "recycling_bereit_fuer_abholung": recycling_bereit_fuer_abholung,
        "recycling_bereit_fuer_halle_2": recycling_bereit_fuer_halle_2,

        "devicecheck_aktiv": devicecheck_aktiv,
        "devicecheck_bereit_fuer_behandlung": devicecheck_bereit_fuer_behandlung,
        "devicecheck_bereit_fuer_abholung": devicecheck_bereit_fuer_abholung,
        "devicecheck_bereit_fuer_halle_2": devicecheck_bereit_fuer_halle_2,

        "unload_total": unload_total,
        "recycling_total": recycling_total,
        "devicecheck_total": devicecheck_total,

        "active_weight_total": overall_total,
    }
