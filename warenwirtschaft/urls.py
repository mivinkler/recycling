from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from warenwirtschaft.views.supplier import SupplierListView, SupplierUpdateView, SupplierDetailView, SupplierCreateView,SupplierDeleteView
from warenwirtschaft.views.customer import CustomerListView, CustomerUpdateView, CustomerDetailView, CustomerCreateView, CustomerDeleteView
from warenwirtschaft.views.delivery import DeliveryUnitsListView, DeliveryUnitDetailView, DeliveryDetailView, DeliveryCreateView, DeliveryUpdateView, DeliveryDeleteView
from warenwirtschaft.views.unload import UnloadListView, UnloadCreateView, UnloadUpdateView, UnloadDeleteView, UnloadDetailView
from warenwirtschaft.views.recycling import RecyclingListView, RecyclingCreateView, RecyclingUpdateView, RecyclingDeleteView, RecyclingDetailView
from warenwirtschaft.views.shipping import ShippingUnitsListView, ShippingDetailView, ShippingCreateView, ShippingUpdateView, ShippingDeleteView

from warenwirtschaft.views.barcode.reusablebarcode_create_view import ReusableBarcodeCreateView
from warenwirtschaft.views.barcode.reusablebarcode_list_view import ReusableBarcodeListView
from warenwirtschaft.views.barcode.reuseblebarcode_detail_view import ReusableBarcodeDetailView
from warenwirtschaft.views.barcode.barcode_print_view import BarcodePrintView


urlpatterns = [
    path('supplier/list/', SupplierListView.as_view(), name='supplier_list'),
    path('supplier/detail/<int:pk>/', SupplierDetailView.as_view(), name='supplier_detail'),
    path('supplier/create/', SupplierCreateView.as_view(), name='supplier_create'),
    path('supplier/update/<int:pk>/', SupplierUpdateView.as_view(), name='supplier_update'),
    path('supplier/delete/<int:pk>/', SupplierDeleteView.as_view(), name='supplier_delete'),

    path('customer/list/', CustomerListView.as_view(), name='customer_list'),
    path('customer/detail/<int:pk>/', CustomerDetailView.as_view(), name='customer_detail'),
    path('customer/create/', CustomerCreateView.as_view(), name='customer_create'),
    path('customer/update/<int:pk>/', CustomerUpdateView.as_view(), name='customer_update'),
    path('customer/delete/<int:pk>/', CustomerDeleteView.as_view(), name='customer_delete'),

    path('delivery/units/', DeliveryUnitsListView.as_view(), name='delivery_list'),
    path('delivery/detail/<int:pk>/', DeliveryDetailView.as_view(), name='delivery_detail'),
    path('delivery-unit/detail/<int:pk>/', DeliveryUnitDetailView.as_view(), name='delivery_unit_detail'),
    path('delivery/create/', DeliveryCreateView.as_view(), name='delivery_create'),
    path('delivery/update/<int:pk>/', DeliveryUpdateView.as_view(), name='delivery_update'),
    path('delivery/delete/<int:pk>/', DeliveryDeleteView.as_view(), name='delivery_delete'),

    path('unload/list/', UnloadListView.as_view(), name='unload_list'),
    path('unload/create/', UnloadCreateView.as_view(), name='unload_create'),
    path('unload/update/<int:pk>/', UnloadUpdateView.as_view(), name='unload_update'),
    path('unload/delete/<int:pk>/', UnloadDeleteView.as_view(), name='unload_delete'),
    path('unload/detail/<int:pk>/', UnloadDetailView.as_view(), name='unload_detail'),

    path('recycling/list/', RecyclingListView.as_view(), name='recycling_list'),
    path('recycling/create/', RecyclingCreateView.as_view(), name='recycling_create'),
    path('recycling/update/<int:pk>/', RecyclingUpdateView.as_view(), name='recycling_update'),
    path('recycling/delete/<int:pk>/', RecyclingDeleteView.as_view(), name='recycling_delete'),
    path('recycling/detail/<int:pk>/', RecyclingDetailView.as_view(), name='recycling_detail'),

    path('shipping/list/', ShippingUnitsListView.as_view(), name='shipping_units_list'),
    path('shipping/detail/<int:pk>/', ShippingDetailView.as_view(), name='shipping_detail'),
    path('shipping/create/', ShippingCreateView.as_view(), name='shipping_create'),
    path('shipping/update/<int:pk>/', ShippingUpdateView.as_view(), name='shipping_update'),
    path('shipping/delete/<int:pk>/', ShippingDeleteView.as_view(), name='shipping_delete'),

    path('reusable-barcodes/create/', ReusableBarcodeCreateView.as_view(), name='reusable_barcode_create'),
    path('reusable-barcodes/list', ReusableBarcodeListView.as_view(), name='reusable_barcode_list'),
    path('reusable-barcodes/detail/<int:pk>/', ReusableBarcodeDetailView.as_view(), name='reusable_barcode_detail'),
    path('barcode/<str:model>/<int:pk>/print/', BarcodePrintView.as_view(), name='barcode_print'),

    path('api/', include('warenwirtschaft.api.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)