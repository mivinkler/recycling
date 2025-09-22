from django.urls import path
from .barcode_delivery_api import BarcodeDeliveryAPI
from .unload_input_api import UnloadInputAPI
from .weight_input_api import WeightInputAPI


urlpatterns = [
    path('unload-input/', UnloadInputAPI.as_view(), name='unload_input_api'),
    path('barcode-delivery-api/', BarcodeDeliveryAPI.as_view(), name='barcode_delivery_api'),
    path('weight-data/', WeightInputAPI.as_view(), name='weight_input_api'),
]