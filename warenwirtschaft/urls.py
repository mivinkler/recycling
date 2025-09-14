from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from warenwirtschaft.views.material import MaterialListView, MaterialCreateView, MaterialUpdateView, MaterialDeleteView
from warenwirtschaft.views.customer import CustomerListView, CustomerUpdateView, CustomerDetailView, CustomerCreateView,CustomerDeleteView
from warenwirtschaft.views.delivery import DeliveryListView, DeliveryDetailBarcodeView, DeliveryDetailWeightView, DeliveryCreateView, DeliveryUpdateView, DeliveryDeleteView, DeliveryUpdateStatusView
from warenwirtschaft.views.unload import UnloadListView, UnloadCreateView, UnloadUpdateItemView, UnloadUpdateView, UnloadDeleteView, UnloadDetailBarcodeView, UnloadDetailWeightView
from warenwirtschaft.views.recycling import RecyclingListView, RecyclingCreateView, RecyclingUpdateView, RecyclingDeleteView, RecyclingDetailView
from warenwirtschaft.views.recycling_weight import RecyclingWeightUpdateView, RecyclingWeightListView
from warenwirtschaft.views.shipping import ShippingListView, ShippingDetailView, ShippingCreateView, ShippingUpdateView, ShippingDeleteView
from warenwirtschaft.views.barcode import ReusableBarcodeListView, ReusableBarcodeDetailView, ReusableBarcodeCreateView, ReusableBarcodeUpdateView, ReusableBarcodeDeleteView, BarcodePrintView



urlpatterns = [
    path('customer/list/', CustomerListView.as_view(), name='customer_list'),
    path('customer/detail/<int:pk>/', CustomerDetailView.as_view(), name='customer_detail'),
    path('customer/create/', CustomerCreateView.as_view(), name='customer_create'),
    path('customer/update/<int:pk>/', CustomerUpdateView.as_view(), name='customer_update'),
    path('customer/delete/<int:pk>/', CustomerDeleteView.as_view(), name='customer_delete'),

    path('delivery/list/', DeliveryListView.as_view(), name='delivery_list'),
    path('delivery/detail/weight/<int:pk>/', DeliveryDetailWeightView.as_view(), name='delivery_detail_weight'),
    path('delivery/detail/barcode/<int:pk>/', DeliveryDetailBarcodeView.as_view(), name='delivery_detail_barcode'),
    path('delivery/create/', DeliveryCreateView.as_view(), name='delivery_create'),
    path('delivery/update/<int:pk>/', DeliveryUpdateView.as_view(), name='delivery_update'),
    path('delivery/delete/<int:pk>/', DeliveryDeleteView.as_view(), name='delivery_delete'),
    path('delivery/status-update/<int:delivery_unit_pk>/', DeliveryUpdateStatusView.as_view(), name='delivery_update_status'),

    path('unload/list/', UnloadListView.as_view(), name='unload_list'),
    path('unload/create/', UnloadCreateView.as_view(), name='unload_create'),
    path('unload/update/<int:delivery_unit_pk>/', UnloadUpdateView.as_view(), name='unload_update'),
    path('unload/update/item/<int:pk>/', UnloadUpdateItemView.as_view(), name='unload_update_item'),
    path('unload/delete/<int:pk>/', UnloadDeleteView.as_view(), name='unload_delete'),
    path('unload/detail/barcode/<int:pk>/', UnloadDetailBarcodeView.as_view(), name='unload_detail_barcode'),
    path('unload/detail/weight/<int:pk>/', UnloadDetailWeightView.as_view(), name='unload_detail_weight'),

    path('recycling/list/', RecyclingListView.as_view(), name='recycling_list'),
    path('recycling/create/', RecyclingCreateView.as_view(), name='recycling_create'),
    path('recycling/update/<int:pk>/', RecyclingUpdateView.as_view(), name='recycling_update'),
    path('recycling/delete/<int:pk>/', RecyclingDeleteView.as_view(), name='recycling_delete'),
    path('recycling/detail/<int:pk>/', RecyclingDetailView.as_view(), name='recycling_detail'),
    
    path('recycling-weight/list', RecyclingWeightListView.as_view(), name='recycling_weight_list'),
    path('recycling-weight/update/<int:pk>/', RecyclingWeightUpdateView.as_view(), name='recycling_weight_update'),

    path('shipping/list/', ShippingListView.as_view(), name='shipping_list'),
    path('shipping/detail/<int:pk>/', ShippingDetailView.as_view(), name='shipping_detail'),
    path('shipping/create/', ShippingCreateView.as_view(), name='shipping_create'),
    path('shipping/update/<int:pk>/', ShippingUpdateView.as_view(), name='shipping_update'),
    path('shipping/delete/<int:pk>/', ShippingDeleteView.as_view(), name='shipping_delete'),

    path('reusable-barcode/list/', ReusableBarcodeListView.as_view(), name='reusable_barcode_list'),
    path('reusable-barcode/detail/<int:pk>/', ReusableBarcodeDetailView.as_view(), name='reusable_barcode_detail'),
    path('reusable-barcode/create/', ReusableBarcodeCreateView.as_view(), name='reusable_barcode_create'),
    path('reusable-barcode/update/<int:pk>/', ReusableBarcodeUpdateView.as_view(), name='reusable_barcode_update'),
    path('reusable-barcode/delete/<int:pk>/', ReusableBarcodeDeleteView.as_view(), name='reusable_barcode_delete'),
    path('barcode/<str:model>/<int:pk>/print/', BarcodePrintView.as_view(), name='barcode_print'),

    path('material/list/', MaterialListView.as_view(), name='material_list'),
    path('material/create/', MaterialCreateView.as_view(), name='material_create'),
    path("material/update/<int:pk>/", MaterialUpdateView.as_view(), name="material_update"),
    path('material/delete/<int:pk>/', MaterialDeleteView.as_view(), name='material_delete'),


    path("api/", include(("warenwirtschaft.api.urls", "warenwirtschaft_api"), namespace="warenwirtschaft_api")),
]