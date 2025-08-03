from django.urls import path
from .views import (
    StaffDashboardView, ProductCreateView, ProductUpdateView,
    OrderUpdateView, FarmToolCreateView, FarmToolUpdateView,
    StaffCreateView, StaffUpdateView, InventoryCreateView, InventoryUpdateView
)

app_name = 'management'

urlpatterns = [
    path('staff_dashboard/', StaffDashboardView.as_view(), name='staff_dashboard'),
    path('product/add/', ProductCreateView.as_view(), name='product_add'),
    path('product/<int:pk>/edit/', ProductUpdateView.as_view(), name='product_edit'),
    path('order/<int:pk>/edit/', OrderUpdateView.as_view(), name='order_edit'),
    path('farm_tool/add/', FarmToolCreateView.as_view(), name='farm_tool_add'),
    path('farm_tool/<int:pk>/edit/', FarmToolUpdateView.as_view(), name='farm_tool_edit'),
    path('staff/add/', StaffCreateView.as_view(), name='staff_add'),
    path('staff/<int:pk>/edit/', StaffUpdateView.as_view(), name='staff_edit'),
    path('inventory/add/', InventoryCreateView.as_view(), name='inventory_add'),
    path('inventory/<int:pk>/edit/', InventoryUpdateView.as_view(), name='inventory_edit'),
]