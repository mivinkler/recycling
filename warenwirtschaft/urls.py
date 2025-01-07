from django.urls import path

from warenwirtschaft.views.supplier.suppliers_list_view import SuppliersListView
from warenwirtschaft.views.supplier.supplier_update_view import SupplierUpdateView
from warenwirtschaft.views.supplier.supplier_detail_view import SupplierDetailView
from warenwirtschaft.views.supplier.supplier_create_view import SupplierCreateView

from warenwirtschaft.views.delivery.deliveries_list_view import DeliveriesListView
from warenwirtschaft.views.delivery.delivery_units_list_view import DeliveryUnitsListView
from warenwirtschaft.views.delivery.delivery_detail_view import DeliveryDetailView
from warenwirtschaft.views.delivery.delivery_create_view import DeliveryCreateView

from warenwirtschaft.views.unloading.unloading_create_view import UnloadingCreateView


urlpatterns = [
    path('suppliers/', SuppliersListView.as_view(), name='suppliers_list'),
    path('supplier/<int:pk>/', SupplierDetailView.as_view(), name='supplier_detail'),
    path('supplier/create/', SupplierCreateView.as_view(), name='supplier_create'),
    path('supplier/update/<int:pk>/', SupplierUpdateView.as_view(), name='supplier_update'),

    path('deliveries', DeliveriesListView.as_view(), name='deliveries_list'),
    path('delivery/units', DeliveryUnitsListView.as_view(), name='delivery_units_list'),
    path('delivery/<int:pk>/', DeliveryDetailView.as_view(), name='delivery_detail'),
    path('delivery/create/', DeliveryCreateView.as_view(), name='delivery_create'),

    path('unloading/create/', UnloadingCreateView.as_view(), name='unloading_create'),
]
