from django.urls import path
from .views import (
    UserDashboardView, ProductDetailView, StaticPageView, AddToCartView,
    CartView, RemoveFromCartView, PlaceOrderView, PaymentView, OrderHistoryView,
    SubmitReviewView, UserProfileView, NotificationView, CustomLoginView,
    CustomLogoutView, RegisterView, OrderCreateView, ProductListView
)

urlpatterns = [
    path('', UserDashboardView.as_view(), name='user_dashboard'),
    path('products/<int:pk>/', ProductDetailView.as_view(), name='product_detail'),
    path('products/', ProductListView.as_view(), name='product_list'),
    path('page/<str:page>/', StaticPageView.as_view(), name='static_page'),
    path('cart/add/<int:pk>/', AddToCartView.as_view(), name='add_to_cart'),
    path('cart/', CartView.as_view(), name='cart'),
    path('cart/remove/<int:pk>/', RemoveFromCartView.as_view(), name='remove_from_cart'),
    path('order/', OrderCreateView.as_view(), name='order_create'),
    path('order/place/', PlaceOrderView.as_view(), name='place_order'),
    path('payment/', PaymentView.as_view(), name='payment'),
    path('order-history/', OrderHistoryView.as_view(), name='order_history'),
    path('products/<int:pk>/review/', SubmitReviewView.as_view(), name='submit_review'),
    path('profile/', UserProfileView.as_view(), name='user_profile'),
    path('notifications/', NotificationView.as_view(), name='notifications'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
    path('register/', RegisterView.as_view(), name='register'),
]