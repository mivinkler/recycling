from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
import sys

from warenwirtschaft.views.material import MaterialListView, MaterialCreateView, MaterialUpdateView, MaterialDeleteView
from warenwirtschaft.views.customer import CustomerListView, CustomerUpdateView, CustomerDetailView, CustomerCreateView,CustomerDeleteView
from warenwirtschaft.views.delivery import DeliveryListView, DeliveryBarcodeView, DeliveryCreateView, DeliveryUnitUpdateView, DeliveryDeleteView
from warenwirtschaft.views.unload import UnloadListView, UnloadSelectView, UnloadCreateView, UnloadUpdateView, UnloadDeleteView, UnloadBarcodeView
from warenwirtschaft.views.recycling import RecyclingListView, RecyclingCreateView, RecyclingUpdateView, RecyclingDeleteView, RecyclingBarcodeView
from warenwirtschaft.views.daily_weight import DailyWeightUpdateView, DailyWeightListView
from warenwirtschaft.views.shipping import ShippingListView, ShippingDetailView, ShippingCreateView, ShippingUpdateView, ShippingDeleteView
from warenwirtschaft.views.barcode import BarcodeGeneratorListView, BarcodeGeneratorDetailView, BarcodeGeneratorCreateView, BarcodeGeneratorUpdateView, BarcodeGeneratorDeleteView
from warenwirtschaft.views.device_check import DeviceCheckUpdateView, DeviceCheckListView, DeviceCheckSelectView
from warenwirtschaft.views.statistic.timeseries_view import TimeSeriesPageView
from warenwirtschaft.views.export_excel import DeliveryExportExcelView, UnloadExportExcelView, RecyclingExportExcelView, ShippingExportExcelView


urlpatterns = [
    # delivery (Wareneingang)
    path('delivery/list/', DeliveryListView.as_view(), name='delivery_list'),
    path('delivery/barcode/<int:pk>/', DeliveryBarcodeView.as_view(), name='delivery_barcode'),
    path('delivery/create/', DeliveryCreateView.as_view(), name='delivery_create'),
    path('<int:delivery_pk>/create/delivery_unit/new', DeliveryUnitUpdateView.as_view(), name='delivery_unit_new'),
    path('<int:delivery_pk>/update/delivery_unit/<int:delivery_unit_pk>/', DeliveryUnitUpdateView.as_view(), name='delivery_unit_update'),
    path('delivery/delete/<int:pk>/', DeliveryDeleteView.as_view(), name='delivery_delete'),

    # unload (Vorsortierung)
    path('unload/list/', UnloadListView.as_view(), name='unload_list'),
    path("unload/select/", UnloadSelectView.as_view(), name="unload_select"),
    path('<int:delivery_unit_pk>/create/unload', UnloadCreateView.as_view(), name='unload_create'),
    path('<int:delivery_unit_pk>/update/unload/<int:unload_pk>/', UnloadUpdateView.as_view(), name='unload_update'),
    path('<int:delivery_unit_pk>/delete/unload/<int:unload_pk>/', UnloadDeleteView.as_view(), name='unload_delete'),
    path('barcode/unload/<int:pk>/', UnloadBarcodeView.as_view(), name='unload_barcode'),

    # recycling (Zerlegung)
    path('recycling/list/', RecyclingListView.as_view(), name='recycling_list'),
    path('recycling/create/', RecyclingCreateView.as_view(), name='recycling_create'),
    path('recycling/update/<int:recycling_pk>/', RecyclingUpdateView.as_view(), name='recycling_update'),
    path('recycling/delete<int:recycling_pk>/', RecyclingDeleteView.as_view(), name='recycling_delete'),
    path('recycling/barcode/<int:pk>/', RecyclingBarcodeView.as_view(), name='recycling_barcode'),
    
    # daily-weight (Tägliches wiegen)
    path('daily-weight/list', DailyWeightListView.as_view(), name='daily_weight_list'),
    path('daily-weight/update/<str:model>/<int:pk>/', DailyWeightUpdateView.as_view(), name='daily_weight_update'),

    # device-check (Halle 2)
    path('device-check/create/<int:unload_pk>/', DeviceCheckUpdateView.as_view(), name='device_check_update'),
    path('device-check/list/', DeviceCheckListView.as_view(), name='device_check_list'),
    path('device-check/select/', DeviceCheckSelectView.as_view(), name='device_check_select'),

    # shipping (Abholung)
    path('shipping/list/', ShippingListView.as_view(), name='shipping_list'),
    path('shipping/detail/<int:pk>/', ShippingDetailView.as_view(), name='shipping_detail'),
    path('shipping/create/', ShippingCreateView.as_view(), name='shipping_create'),
    path('shipping/update/<int:pk>/', ShippingUpdateView.as_view(), name='shipping_update'),
    path('shipping/delete/<int:pk>/', ShippingDeleteView.as_view(), name='shipping_delete'),

    # customer (Kunden)
    path('customer/list/', CustomerListView.as_view(), name='customer_list'),
    path('customer/detail/<int:pk>/', CustomerDetailView.as_view(), name='customer_detail'),
    path('customer/create/', CustomerCreateView.as_view(), name='customer_create'),
    path('customer/update/<int:pk>/', CustomerUpdateView.as_view(), name='customer_update'),
    path('customer/delete/<int:pk>/', CustomerDeleteView.as_view(), name='customer_delete'),

    # material
    path('material/list/', MaterialListView.as_view(), name='material_list'),
    path('material/create/', MaterialCreateView.as_view(), name='material_create'),
    path("material/update/<int:pk>/", MaterialUpdateView.as_view(), name="material_update"),
    path('material/delete/<int:pk>/', MaterialDeleteView.as_view(), name='material_delete'),
    
    # barcode-generator
    path('barcode-generator/list/', BarcodeGeneratorListView.as_view(), name='barcode_generator_list'),
    path('barcode-generator/detail/<int:pk>/', BarcodeGeneratorDetailView.as_view(), name='barcode_generator_detail'),
    path('barcode-generator/create/', BarcodeGeneratorCreateView.as_view(), name='barcode_generator_create'),
    path('barcode-generator/update/<int:pk>/', BarcodeGeneratorUpdateView.as_view(), name='barcode_generator_update'),
    path('barcode-generator/delete/<int:pk>/', BarcodeGeneratorDeleteView.as_view(), name='barcode_generator_delete'),

    # excel herunterladen
    path('delivery-export-excel/', DeliveryExportExcelView.as_view(), name='delivery_export_excel'),
    path('unload-export-excel/', UnloadExportExcelView.as_view(), name='unload_export_excel'),
    path('recycling-export-excel/', RecyclingExportExcelView.as_view(), name='recycling_export_excel'),
    path('shipping-export-excel/', ShippingExportExcelView.as_view(), name='shipping_export_excel'),

    # statistic
    path("statistic/", TimeSeriesPageView.as_view(), name="statistic"),

    path("api/", include(("warenwirtschaft.api.urls", "warenwirtschaft_api"), namespace="warenwirtschaft_api")),
]
