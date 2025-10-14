from datetime import date
from django.shortcuts import render
from django.views import View

from warenwirtschaft.forms.timeseries_form import TimeSeriesFilterForm

class TimeSeriesPageView(View):
    template_name = "statistic/timeseries.html"

    @staticmethod
    def _default_range():
        # Standard: letzte 12 Monate (ab 1. des Vorjahresmonats bis heute)
        today = date.today()
        start = date(today.year - 1, today.month, 1)
        return start, today

    def get(self, request):
        start, end = self._default_range()
        form = TimeSeriesFilterForm(initial={"date_from": start, "date_to": end})
        
        context = {
            "form": form,
            "selected_menu": "statistic",  # <-- добавлено
        }

        return render(request, self.template_name, context)
