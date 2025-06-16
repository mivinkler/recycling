from django.urls import path
from .unload_input_api import UnloadInputAPI
from .barcode_data_api import BarcodeDataAPI

urlpatterns = [
    path('unload-input/', UnloadInputAPI.as_view(), name='unload_input_api'),
    path('barcode-data/', BarcodeDataAPI.as_view(), name='barcode_data_api'),
]