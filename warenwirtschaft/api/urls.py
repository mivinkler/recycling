from django.urls import path
from .delivery_input_api import DeliveryInputAPI
from .unload_input_api import UnloadInputAPI
from .weight_input_api import WeightInputAPI


urlpatterns = [
    path('unload-input/', UnloadInputAPI.as_view(), name='unload_input_api'),
    path('delivery-input-api/', DeliveryInputAPI.as_view(), name='delivery_input_api'),
    path('weight-data/', WeightInputAPI.as_view(), name='weight_input_api'),
]