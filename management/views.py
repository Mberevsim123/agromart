from django.views.generic import TemplateView, CreateView, UpdateView
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib import messages
from django.urls import reverse_lazy
from store.models import Product, Order, FarmTool, Staff, Inventory, User
from .forms import ProductForm, OrderForm, FarmToolForm, StaffForm, InventoryForm
from django.db.models import Count, Sum, F

class StaffDashboardView(UserPassesTestMixin, TemplateView):
    template_name = 'management/staff_dashboard.html'

    def test_func(self):
        return self.request.user.is_staff

    def handle_no_permission(self):
        messages.error(self.request, "You must be a staff member to access the dashboard.")
        return super().handle_no_permission()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_products'] = Product.objects.filter(is_active=True).count()
        context['low_stock_products'] = Product.objects.filter(is_active=True, stock__lte=10).count()
        context['total_orders'] = Order.objects.count()
        context['pending_orders'] = Order.objects.filter(status='pending').count()
        context['total_staff'] = Staff.objects.filter(is_active=True).count()
        context['recent_orders'] = Order.objects.select_related('user').order_by('-ordered_at')[:5]
        context['low_stock_list'] = Product.objects.filter(is_active=True, stock__lte=10).select_related('category')[:5]
        context['top_customers'] = User.objects.filter(customer_profile__isnull=False).annotate(
            order_count=Count('orders'),
            total_spent=Sum(F('orders__total_price'))
        ).order_by('-total_spent')[:5]
        context['inventory_items'] = Inventory.objects.select_related('product', 'farm_tool', 'location')[:5]
        context['farm_tools'] = FarmTool.objects.filter(is_operational=True).select_related('location')[:5]
        return context

class ProductCreateView(UserPassesTestMixin, CreateView):
    model = Product
    form_class = ProductForm
    template_name = 'management/product_form.html'
    success_url = reverse_lazy('management:staff_dashboard')

    def test_func(self):
        return self.request.user.is_staff

    def form_valid(self, form):
        messages.success(self.request, f"Product '{form.instance.name}' created successfully.")
        return super().form_valid(form)

class ProductUpdateView(UserPassesTestMixin, UpdateView):
    model = Product
    form_class = ProductForm
    template_name = 'management/product_form.html'
    success_url = reverse_lazy('management:staff_dashboard')

    def test_func(self):
        return self.request.user.is_staff

    def form_valid(self, form):
        messages.success(self.request, f"Product '{form.instance.name}' updated successfully.")
        return super().form_valid(form)

class OrderUpdateView(UserPassesTestMixin, UpdateView):
    model = Order
    form_class = OrderForm
    template_name = 'management/order_form.html'
    success_url = reverse_lazy('management:staff_dashboard')

    def test_func(self):
        return self.request.user.is_staff

    def form_valid(self, form):
        messages.success(self.request, f"Order #{form.instance.id} updated successfully.")
        return super().form_valid(form)

class FarmToolCreateView(UserPassesTestMixin, CreateView):
    model = FarmTool
    form_class = FarmToolForm
    template_name = 'management/farm_tool_form.html'
    success_url = reverse_lazy('management:staff_dashboard')

    def test_func(self):
        return self.request.user.is_staff

    def form_valid(self, form):
        messages.success(self.request, f"Farm tool '{form.instance.name}' created successfully.")
        return super().form_valid(form)

class FarmToolUpdateView(UserPassesTestMixin, UpdateView):
    model = FarmTool
    form_class = FarmToolForm
    template_name = 'management/farm_tool_form.html'
    success_url = reverse_lazy('management:staff_dashboard')

    def test_func(self):
        return self.request.user.is_staff

    def form_valid(self, form):
        messages.success(self.request, f"Farm tool '{form.instance.name}' updated successfully.")
        return super().form_valid(form)

class StaffCreateView(UserPassesTestMixin, CreateView):
    model = Staff
    form_class = StaffForm
    template_name = 'management/staff_form.html'
    success_url = reverse_lazy('management:staff_dashboard')

    def test_func(self):
        return self.request.user.is_staff

    def form_valid(self, form):
        messages.success(self.request, f"Staff '{form.instance.user.username}' created successfully.")
        return super().form_valid(form)

class StaffUpdateView(UserPassesTestMixin, UpdateView):
    model = Staff
    form_class = StaffForm
    template_name = 'management/staff_form.html'
    success_url = reverse_lazy('management:staff_dashboard')

    def test_func(self):
        return self.request.user.is_staff

    def form_valid(self, form):
        messages.success(self.request, f"Staff '{form.instance.user.username}' updated successfully.")
        return super().form_valid(form)

class InventoryCreateView(UserPassesTestMixin, CreateView):
    model = Inventory
    form_class = InventoryForm
    template_name = 'management/inventory_form.html'
    success_url = reverse_lazy('management:staff_dashboard')

    def test_func(self):
        return self.request.user.is_staff

    def form_valid(self, form):
        item = form.instance.product or form.instance.farm_tool
        messages.success(self.request, f"Inventory for '{item}' created successfully.")
        return super().form_valid(form)

class InventoryUpdateView(UserPassesTestMixin, UpdateView):
    model = Inventory
    form_class = InventoryForm
    template_name = 'management/inventory_form.html'
    success_url = reverse_lazy('management:staff_dashboard')

    def test_func(self):
        return self.request.user.is_staff

    def form_valid(self, form):
        item = form.instance.product or form.instance.farm_tool
        messages.success(self.request, f"Inventory for '{item}' updated successfully.")
        return super().form_valid(form)