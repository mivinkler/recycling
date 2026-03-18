from django import template
from django.db.models import Sum
from warenwirtschaft.models_common.choices import StatusChoices

from warenwirtschaft.models import DeliveryUnit, Unload, Recycling, HalleZwei

register = template.Library()

@register.inclusion_tag("components/header_active_weights.html")
def header_active_weights():
    def get_weight_by_status(model, status, weight_field="weight"):
        return (
            model.objects
            .filter(status=status)
            .aggregate(total=Sum(weight_field))
            .get("total")
            or 0
        )

    
    delivery_aktiv = get_weight_by_status(DeliveryUnit, StatusChoices.AKTIV_IN_VORSORTIERUNG)
    delivery_wartet = get_weight_by_status(DeliveryUnit, StatusChoices.WARTET_AUF_VORSORTIERUNG)
    delivery_abholbereit = get_weight_by_status(DeliveryUnit, StatusChoices.WARTET_AUF_ABHOLUNG)

    unload_aktiv = get_weight_by_status(Unload, StatusChoices.AKTIV_IN_ZERLEGUNG)
    unload_wartet = get_weight_by_status(Unload, StatusChoices.WARTET_AUF_ZERLEGUNG)
    unload_abholbereit = get_weight_by_status(Unload, StatusChoices.WARTET_AUF_ABHOLUNG)

    recycling_aktiv = get_weight_by_status(Recycling, StatusChoices.AKTIV_IN_ZERLEGUNG)
    recycling_wartet = get_weight_by_status(Recycling, StatusChoices.WARTET_AUF_ZERLEGUNG)
    recycling_abholbereit = get_weight_by_status(Recycling, StatusChoices.WARTET_AUF_ABHOLUNG)

    halle_zwei_aktiv = get_weight_by_status(
        HalleZwei, StatusChoices.AKTIV_IN_HALLE_ZWEI, "delivery_unit__weight"
    )
    halle_zwei_wartet = get_weight_by_status(
        HalleZwei, StatusChoices.WARTET_AUF_HALLE_ZWEI, "delivery_unit__weight"
    )
    halle_zwei_abholbereit = get_weight_by_status(
        HalleZwei, StatusChoices.WARTET_AUF_ABHOLUNG, "delivery_unit__weight"
    )

    delivery_total = delivery_aktiv + delivery_wartet + delivery_abholbereit
    unload_total = unload_aktiv + unload_wartet + unload_abholbereit
    recycling_total = recycling_aktiv + recycling_wartet + recycling_abholbereit
    halle_zwei_total = halle_zwei_aktiv + halle_zwei_wartet + halle_zwei_abholbereit
    
    weight_total = delivery_total + unload_total + recycling_total + halle_zwei_total


    ready_total = delivery_abholbereit + unload_abholbereit + recycling_abholbereit + halle_zwei_abholbereit
    activ_total = delivery_aktiv + unload_aktiv + recycling_aktiv + halle_zwei_aktiv
    wartet_total = delivery_wartet + unload_wartet + recycling_wartet + halle_zwei_wartet


    return {
        "delivery_aktiv": delivery_aktiv,
        "delivery_wartet": delivery_wartet,
        "delivery_abholbereit": delivery_abholbereit,

        "unload_aktiv": unload_aktiv,
        "unload_wartet": unload_wartet,
        "unload_abholbereit": unload_abholbereit,

        "recycling_aktiv": recycling_aktiv,
        "recycling_wartet": recycling_wartet,
        "recycling_abholbereit": recycling_abholbereit,

        "halle_zwei_aktiv": halle_zwei_aktiv,
        "halle_zwei_wartet": halle_zwei_wartet,
        "halle_zwei_abholbereit": halle_zwei_abholbereit,

        "delivery_total": delivery_total,
        "unload_total": unload_total,
        "recycling_total": recycling_total,
        "halle_zwei_total": halle_zwei_total,

        "active_weight_total": activ_total,
        "ready_for_shipping_total": ready_total,
        "expect_total": wartet_total,

        "weight_total": weight_total,
    }
