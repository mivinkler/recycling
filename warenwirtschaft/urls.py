from django.urls import path

from warenwirtschaft.views.supplier.supplier_list_view import SupplierListView
from warenwirtschaft.views.supplier.supplier_update_view import SupplierUpdateView
from warenwirtschaft.views.supplier.supplier_detail_view import SupplierDetailView
from warenwirtschaft.views.supplier.supplier_create_view import SupplierCreateView
from warenwirtschaft.views.supplier.supplier_delete_view import SupplierDeleteView

from warenwirtschaft.views.delivery.delivery_units_list_view import DeliveryUnitsListView
from warenwirtschaft.views.delivery.delivery_detail_view import DeliveryDetailView
from warenwirtschaft.views.delivery.delivery_create_view import DeliveryCreateView
from warenwirtschaft.views.delivery.delivery_update_view import DeliveryUpdateView

from warenwirtschaft.views.unload.unload_list_view import UnloadListView
from warenwirtschaft.views.unload.unload_create_view import UnloadCreateView
from warenwirtschaft.views.unload.unload_update_view import UnloadUpdateView


urlpatterns = [
    path('', SupplierListView.as_view(), name='home'),

    path('supplier/list/', SupplierListView.as_view(), name='suppliers_list'),
    path('supplier/<int:pk>/', SupplierDetailView.as_view(), name='supplier_detail'),
    path('supplier/create/', SupplierCreateView.as_view(), name='supplier_create'),
    path('supplier/update/<int:pk>/', SupplierUpdateView.as_view(), name='supplier_update'),
    path('supplier/delete/<int:pk>/', SupplierDeleteView.as_view(), name='supplier_delete'),

    path('delivery/units/', DeliveryUnitsListView.as_view(), name='delivery_units_list'),
    path('delivery/<int:pk>/', DeliveryDetailView.as_view(), name='delivery_detail'),
    path('delivery/create/', DeliveryCreateView.as_view(), name='delivery_create'),
    path('delivery/update/<int:pk>/', DeliveryUpdateView.as_view(), name='delivery_update'),


    path('unload/list/', UnloadListView.as_view(), name='unload_list'),
    path('unload/create/', UnloadCreateView.as_view(), name='unload_create'),
    path('unload/deliveryunit/update/<int:pk>/', UnloadUpdateView.as_view(), name='deliveryunit_update'),
]
