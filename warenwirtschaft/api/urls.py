from django.urls import path
from .weight_input_api import WeightInputAPI
from .statistic.timeseries_api import TimeSeriesApiView


urlpatterns = [
    path('weight-data/', WeightInputAPI.as_view(), name='weight_input_api'),
    
    path("stats/timeseries/", TimeSeriesApiView.as_view(), name="timeseries"),
]
