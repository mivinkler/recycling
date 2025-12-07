# warenwirtschaft/views/daily_weight.py

from django.shortcuts import render
from django.utils.timezone import localdate
from warenwirtschaft.models import UnloadWeight, RecyclingWeight


def daily_weight_list_view(request):
    """
    Zeigt alle heutigen Gewichts- und Statusänderungen
    für Unload und Recycling auf einer Seite an.
    """

    today = localdate()

    # Historie-Einträge für heute (Datum basiert auf created_at)
    unload_weights = (
        UnloadWeight.objects
        .filter(created_at__date=today)
        .select_related("unload")
    )
    recycling_weights = (
        RecyclingWeight.objects
        .filter(created_at__date=today)
        .select_related("recycling")
    )

    context = {
        "unload_weights": unload_weights,
        "recycling_weights": recycling_weights,
        "date": today,
    }
    return render(request, "daily_weight_list.html", context)
