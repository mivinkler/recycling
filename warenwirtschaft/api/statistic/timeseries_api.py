# API: JSON-Endpunkt für Zeitreihen (Chart.js)
from __future__ import annotations
from datetime import date
from django.http import JsonResponse, HttpRequest
from django.views import View

from warenwirtschaft.services.timeseries_service import (
    TimeSeriesParams,
    timeseries_weight,
)

def _parse_iso_date(val: str | None, default: date) -> date:
    # Erwartet 'YYYY-MM-DD' (von <input type="date">); fällt auf default zurück
    if not val:
        return default
    try:
        return date.fromisoformat(val)
    except Exception:
        return default

def _parse_int(val: str | None) -> int | None:
    # Leer → None; ungültig → None
    if not val:
        return None
    try:
        return int(val)
    except Exception:
        return None

class TimeSeriesApiView(View):
    # GET /warenwirtschaft/api/stats/timeseries/
    def get(self, request: HttpRequest) -> JsonResponse:
        today = date.today()
        default_from = date(today.year - 1, today.month, 1)
        default_to = today

        d_from = _parse_iso_date(request.GET.get("from"), default_from)
        d_to   = _parse_iso_date(request.GET.get("to"), default_to)
        if d_from > d_to:
            d_from, d_to = d_to, d_from

        params = TimeSeriesParams(
            date_from=d_from,
            date_to=d_to,
            customer_id=_parse_int(request.GET.get("customer_id")),
            material_id=_parse_int(request.GET.get("material_id")),
            granularity=(request.GET.get("granularity") or "auto").lower(),
        )
        data = timeseries_weight(params)
        return JsonResponse(data, json_dumps_params={"ensure_ascii": False})
