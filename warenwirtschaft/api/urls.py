from django.urls import path
from .unload_input import UnloadInputAPI

urlpatterns = [
    path('unload-input/', UnloadInputAPI.as_view(), name='unload_input_api'),
]