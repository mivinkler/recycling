from django.urls import path
from warenwirtschaft import views


urlpatterns = [
    path("eingang/", views.eingang, name="eingang"),
    path("suppliers/", views.suppliers, name="suppliers"),
    path('supplier/update/<int:pk>/', views.supplier_update, name='supplier_update'),
    path('supplier/deliveries/<int:pk>/', views.supplier_deliveries, name='supplier_deliveries'),
    path('delivery/', views.delivery, name='delivery'),
    path('delivery_units/', views.delivery_units, name='delivery_units'),
]