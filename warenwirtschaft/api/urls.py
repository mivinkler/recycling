from django.urls import path
from .barcode_delivery_api import BarcodeDeliveryAPI
from .barcode_unload_api import BarcodeUnloadAPI
from .weight_input_api import WeightInputAPI


urlpatterns = [
    path('barcode-unload-api/', BarcodeUnloadAPI.as_view(), name='barcode_unload_api'),
    path('barcode-delivery-api/', BarcodeDeliveryAPI.as_view(), name='barcode_delivery_api'),
    path('weight-data/', WeightInputAPI.as_view(), name='weight_input_api'),
]