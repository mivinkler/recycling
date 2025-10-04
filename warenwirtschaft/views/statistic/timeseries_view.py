# 🇩🇪 Views: HTML-Seite (Report) + JSON-API für Chart.js
from datetime import date
from django.http import JsonResponse
from django.shortcuts import render
from django.views import View

from warenwirtschaft.forms.timeseries import TimeSeriesFilterForm
from warenwirtschaft.services.timeseries_service import (
    TimeSeriesParams, timeseries_weight
)

class TimeSeriesPageView(View):
    template_name = "statistic/timeseries.html"

    def get_default_range(self):
        # 🇩🇪 Standard: letzte 12 Monate (inkl. heutigem Datum)
        today = date.today()
        start = date(today.year - 1, today.month, 1)
        end = today
        return start, end

    def get(self, request):
        start, end = self.get_default_range()
        form = TimeSeriesFilterForm(initial={"date_from": start, "date_to": end})
        return render(request, self.template_name, {"form": form})

class TimeSeriesApiView(View):
    # 🇩🇪 JSON für Chart.js
    def get(self, request):
        def parse_date(name, default):
            v = request.GET.get(name)
            return date.fromisoformat(v) if v else default

        today = date.today()
        default_from = date(today.year - 1, today.month, 1)
        default_to = today

        p = TimeSeriesParams(
            date_from=parse_date("from", default_from),
            date_to=parse_date("to", default_to),
            customer_id=int(request.GET["customer_id"]) if request.GET.get("customer_id") else None,
            material_id=int(request.GET["material_id"]) if request.GET.get("material_id") else None,
            granularity=request.GET.get("granularity", "auto"),
        )
        data = timeseries_weight(p)
        return JsonResponse(data, json_dumps_params={"ensure_ascii": False})
