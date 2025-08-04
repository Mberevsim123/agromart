from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, FormView, CreateView, View
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib import messages
from django.db.models import Sum, F
from django.db import transaction
from django.utils import timezone
from decimal import Decimal
from .models import (
    Product, FarmingProduct, Order, OrderItem, PaymentTransaction, Notification, DeliveryTracking,
    Report, AnnualProduction, Category, UserProfile, Review, Customer, Cart, BusinessLocation
)
from .forms import (UserProfileForm, UserInfoForm, UserPasswordChangeForm, ReviewForm,
    ProductFilterForm, PaymentForm, OrderForm, RegisterForm, AddToCartForm, ContactForm
     )
# Static Pages View
class StaticPageView(View):
    template_map = {
        'about': 'store/about.html',
        'farming_experience': 'store/farming_experience.html',
        'types_of_farming': 'store/types_of_farming.html',
        'annual_report': 'store/annual_report.html',
        'annual_cultivation': 'store/annual_cultivation.html',
        'harvest_report': 'store/harvest_report.html',
        'contact': 'store/contact.html',
        'faq': 'store/faq.html',
    }

    def get(self, request, page):
        template = self.template_map.get(page, 'store/404.html')
        context = {}
        if page == 'types_of_farming':
            context['categories'] = Category.objects.all()
        elif page == 'annual_report':
            context['reports'] = Report.objects.filter(report_type__in=['sales', 'production', 'profit_loss'])[:5]
        elif page == 'annual_cultivation':
            context['productions'] = AnnualProduction.objects.select_related('product__product', 'farm').order_by('-year')[:10]
        elif page == 'harvest_report':
            context['farming_products'] = FarmingProduct.objects.select_related('product').filter(harvest_date__isnull=False).order_by('-harvest_date')[:10]
        elif page == 'contact':
            context['form'] = ContactForm()
        return render(request, template, context)

    def post(self, request, page):
        if page == 'contact':
            form = ContactForm(request.POST)
            if form.is_valid():
                # Simulate saving contact message (e.g., to a model or email)
                messages.success(request, "Thank you for your message! We'll get back to you soon.")
                return redirect('static_page', page='contact')
            else:
                messages.error(request, "Please correct the errors in the form.")
                return render(request, 'store/contact.html', {'form': form})
        return redirect('static_page', page=page)

# User Dashboard
class UserDashboardView(ListView):
    template_name = 'store/index.html'
    context_object_name = 'products'
    paginate_by = 12  # 4 rows x 3 columns

    def get_queryset(self):
        queryset = Product.objects.filter(is_active=True).select_related('category')
        form = ProductFilterForm(self.request.GET)
        if form.is_valid():
            category = form.cleaned_data.get('category')
            search_query = form.cleaned_data.get('search_query')
            if category:
                queryset = queryset.filter(category=category)
            if search_query:
                queryset = queryset.filter(name__icontains=search_query)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = ProductFilterForm(self.request.GET)
        if self.request.user.is_authenticated:
            context['notifications'] = Notification.objects.filter(user=self.request.user).order_by('-created_at')[:5]
            context['cart_items'] = Cart.objects.filter(user=self.request.user).count()
        else:
            context['notifications'] = []
            context['cart_items'] = 0
        return context

class ProductListView(ListView):
    template_name = 'store/product_list.html'
    context_object_name = 'products'
    paginate_by = 20

    def get_queryset(self):
        return Product.objects.filter(is_active=True).select_related('category').order_by('id')

# Product Detail
class ProductDetailView(DetailView):
    model = Product
    template_name = 'store/product_detail.html'
    context_object_name = 'product'

    def get_queryset(self):
        return Product.objects.select_related('category').prefetch_related('reviews')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context['farming_product'] = self.object.farming_product
        except Product.farming_product.RelatedObjectDoesNotExist:
            context['farming_product'] = None
        context['reviews'] = self.object.reviews.filter(is_approved=True)
        if self.request.user.is_authenticated:
            context['review_form'] = ReviewForm()
            context['cart_form'] = AddToCartForm(product=self.object)
        return context

# Add to Cart
class AddToCartView(LoginRequiredMixin, View):
    def post(self, request, pk):
        product = get_object_or_404(Product, pk=pk, is_active=True)
        form = AddToCartForm(request.POST, product=product)
        if form.is_valid():
            quantity = form.cleaned_data['quantity']
            cart_item, created = Cart.objects.get_or_create(
                user=request.user,
                product=product,
                defaults={'quantity': quantity}
            )
            if not created:
                new_quantity = cart_item.quantity + quantity
                if new_quantity > product.stock:
                    messages.error(request, f"Cannot add {quantity} more. Only {product.stock - cart_item.quantity} left in stock.")
                    return redirect('product_detail', pk=pk)
                cart_item.quantity = new_quantity
                cart_item.save()
            messages.success(request, f"{product.name} added to cart.")
            return redirect('cart')
        messages.error(request, "Invalid quantity.")
        return redirect('product_detail', pk=pk)

# Remove from Cart
class RemoveFromCartView(LoginRequiredMixin, View):
    def post(self, request, pk):
        cart_item = get_object_or_404(Cart, pk=pk, user=request.user)
        product_name = cart_item.product.name
        cart_item.delete()
        messages.success(request, f"{product_name} removed from cart.")
        return redirect('cart')

# View Cart
class CartView(LoginRequiredMixin, ListView):
    template_name = 'store/cart.html'
    context_object_name = 'cart_items'

    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user).select_related('product__category')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart_items = self.get_queryset()
        context['total_price'] = cart_items.aggregate(total=Sum(F('product__price') * F('quantity')))['total'] or Decimal('0.00')
        context['order_form'] = OrderForm(user=self.request.user)
        return context

# Place Order (Cart-based)
class PlaceOrderView(LoginRequiredMixin, View):
    def post(self, request):
        cart_items = Cart.objects.filter(user=self.request.user).select_related('product')
        order_form = OrderForm(request.POST, user=self.request.user)
        if not cart_items:
            messages.error(request, "Your cart is empty.")
            return redirect('cart')

        if not order_form.is_valid():
            messages.error(request, "Invalid shipping details.")
            return redirect('cart')

        # Validate stock
        for item in cart_items:
            if item.quantity > item.product.stock:
                messages.error(request, f"Insufficient stock for {item.product.name}. Only {item.product.stock} available.")
                return redirect('cart')

        try:
            with transaction.atomic():
                # Create or get UserProfile
                user_profile, created = UserProfile.objects.get_or_create(user=self.request.user)
                order = Order.objects.create(
                    user=self.request.user,
                    location=BusinessLocation.objects.first(),  # Placeholder, update with user-selected location
                    total_price=Decimal('0.00'),
                    status='pending',
                    shipping_address=order_form.cleaned_data['shipping_address'],
                    shipping_city=order_form.cleaned_data['shipping_city'],
                    shipping_country=order_form.cleaned_data['shipping_country'],
                    shipping_postal_code=order_form.cleaned_data['shipping_postal_code']
                )

                # Create OrderItems and update stock
                total_price = Decimal('0.00')
                for item in cart_items:
                    subtotal = item.product.price * item.quantity
                    OrderItem.objects.create(
                        order=order,
                        product=item.product,
                        quantity=item.quantity,
                        unit_price=item.product.price,
                        subtotal=subtotal
                    )
                    item.product.stock -= item.quantity
                    item.product.save()
                    total_price += subtotal
                order.total_price = total_price
                order.save()

                # Create Notification
                Notification.objects.create(
                    user=self.request.user,
                    message=f"Order #{order.id} placed successfully!",
                    type='order_update',
                    order=order
                )

                # Create DeliveryTracking
                DeliveryTracking.objects.create(
                    order=order,
                    tracking_number=f"TRK{order.id}{int(timezone.now().timestamp())}",
                    carrier="Default Carrier",
                    status='preparing'
                )

                # Update Customer loyalty points
                customer, created = Customer.objects.get_or_create(user=self.request.user)
                customer.loyalty_points += int(total_price // 10)  # 1 point per $10
                customer.last_purchase = timezone.now()
                customer.preferred_payment_method = order_form.data.get('payment_method', customer.preferred_payment_method)
                customer.save()

                # Clear cart
                cart_items.delete()

                messages.success(request, f"Order #{order.id} placed successfully! Proceed to payment.")
                return redirect('payment')
        except Exception as e:
            messages.error(request, f"Failed to place order: {str(e)}")
            return redirect('cart')

# Place Order (Direct Product Selection)
class OrderCreateView(LoginRequiredMixin, FormView):
    login_url = '/login/'  # Add this
    template_name = 'store/order.html'
    form_class = OrderForm
    success_url = reverse_lazy('payment')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['products'] = Product.objects.filter(is_active=True).select_related('category')
        return context

    def form_valid(self, form):
        selected_products = []
        total_price = Decimal('0.00')
        for key, value in self.request.POST.items():
            if key.startswith('quantity_') and int(value) > 0:
                product_id = key.replace('quantity_', '')
                product = get_object_or_404(Product, pk=product_id, is_active=True)
                quantity = int(value)
                if quantity > product.stock:
                    messages.error(self.request, f"Insufficient stock for {product.name}. Only {product.stock} available.")
                    return redirect('order_create')
                selected_products.append((product, quantity))
                total_price += product.price * quantity

        if not selected_products:
            messages.error(self.request, "Please select at least one product.")
            return redirect('order_create')

        try:
            with transaction.atomic():
                # Create or get UserProfile
                user_profile, created = UserProfile.objects.get_or_create(user=self.request.user)
                order = Order.objects.create(
                    user=self.request.user,
                    location=BusinessLocation.objects.first(),  # Placeholder, update with user-selected location
                    total_price=total_price,
                    status='pending',
                    shipping_address=form.cleaned_data['shipping_address'],
                    shipping_city=form.cleaned_data['shipping_city'],
                    shipping_country=form.cleaned_data['shipping_country'],
                    shipping_postal_code=form.cleaned_data['shipping_postal_code']
                )

                for product, quantity in selected_products:
                    OrderItem.objects.create(
                        order=order,
                        product=product,
                        quantity=quantity,
                        unit_price=product.price,
                        subtotal=product.price * quantity
                    )
                    product.stock -= quantity
                    product.save()

                Notification.objects.create(
                    user=self.request.user,
                    message=f"Order #{order.id} placed successfully!",
                    type='order_update',
                    order=order
                )

                DeliveryTracking.objects.create(
                    order=order,
                    tracking_number=f"TRK{order.id}{int(timezone.now().timestamp())}",
                    carrier="Default Carrier",
                    status='preparing'
                )

                customer, created = Customer.objects.get_or_create(user=self.request.user)
                customer.loyalty_points += int(total_price // 10)  # 1 point per $10
                customer.last_purchase = timezone.now()
                customer.preferred_payment_method = form.data.get('payment_method', customer.preferred_payment_method)
                customer.save()

                messages.success(self.request, f"Order #{order.id} placed successfully! Proceed to payment.")
                return super().form_valid(form)
        except Exception as e:
            messages.error(self.request, f"Failed to place order: {str(e)}")
            return redirect('order_create')

# Payment Processing
class PaymentView(LoginRequiredMixin, FormView):
    template_name = 'store/payment.html'
    form_class = PaymentForm
    success_url = reverse_lazy('order_history')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['order'] = Order.objects.filter(user=self.request.user).order_by('-ordered_at').first()
        context['products'] = Product.objects.filter(is_active=True).select_related('category')
        context['form'] = PaymentForm(user=self.request.user)
        return context

    def form_valid(self, form):
        order = Order.objects.filter(user=self.request.user).order_by('-ordered_at').first()
        if not order:
            messages.error(self.request, "No recent order found. Please place an order first.")
            return redirect('order_create')

        payment_method = form.cleaned_data['payment_method']
        currency = self.request.user.userprofile.preferred_currency or 'USD'

        try:
            with transaction.atomic():
                if payment_method == 'stripe':
                    # Simulate Stripe card payment
                    transaction_id = f"txn_stripe_{order.id}_{int(timezone.now().timestamp())}"
                    gateway = 'stripe'
                    status = 'completed'  # Simulate success
                elif payment_method == 'paypal':
                    # Simulate PayPal card payment
                    transaction_id = f"txn_paypal_{order.id}_{int(timezone.now().timestamp())}"
                    gateway = 'paypal'
                    status = 'completed'  # Simulate success
                elif payment_method == 'bank_transfer':
                    # Simulate SEPA Credit Transfer
                    transaction_id = f"txn_sct_{order.id}_{int(timezone.now().timestamp())}"
                    gateway = 'bank_transfer'
                    status = 'pending'  # Manual verification
                elif payment_method == 'sdd':
                    # Simulate SEPA Direct Debit
                    if not form.cleaned_data['iban'] or not form.cleaned_data['sdd_mandate']:
                        raise ValueError("IBAN and mandate authorization required for SEPA Direct Debit.")
                    transaction_id = f"txn_sdd_{order.id}_{int(timezone.now().timestamp())}"
                    gateway = 'bank_transfer'  # Map SDD to bank_transfer
                    status = 'pending'  # Requires mandate verification

                PaymentTransaction.objects.create(
                    order=order,
                    user=self.request.user,
                    amount=order.total_price,
                    currency=currency,
                    transaction_id=transaction_id,
                    status=status
                )

                # Update Customer preferred payment method
                customer, created = Customer.objects.get_or_create(user=self.request.user)
                customer.preferred_payment_method = payment_method
                customer.save()

                order.status = 'processing' if payment_method in ['stripe', 'paypal'] else 'pending'
                order.save()

                Notification.objects.create(
                    user=self.request.user,
                    message=f"Payment for Order #{order.id} initiated via {payment_method}.",
                    type='order_update',
                    order=order
                )

                messages.success(self.request, f"Payment for Order #{order.id} initiated successfully!")
                return super().form_valid(form)
        except Exception as e:
            messages.error(self.request, f"Payment failed: {str(e)}")
            return redirect('payment')

# Order History
class OrderHistoryView(LoginRequiredMixin, ListView):
    template_name = 'store/order_history.html'
    context_object_name = 'orders'
    paginate_by = 10

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).select_related('location').prefetch_related('items', 'delivery').order_by('-ordered_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['delivery_statuses'] = {order.id: order.delivery.first() for order in context['orders']}
        return context

# Submit Review
class SubmitReviewView(LoginRequiredMixin, FormView):
    form_class = ReviewForm
    template_name = 'store/product_detail.html'

    def form_valid(self, form):
        product = get_object_or_404(Product, pk=self.kwargs['pk'])
        Review.objects.create(
            product=product,
            user=self.request.user,
            rating=form.cleaned_data['rating'],
            comment=form.cleaned_data['comment']
        )
        Notification.objects.create(
            user=self.request.user,
            message=f"Review submitted for {product.name}",
            type='system'
        )
        messages.success(self.request, "Review submitted successfully.")
        return redirect('product_detail', pk=product.id)

    def get_success_url(self):
        return reverse_lazy('product_detail', kwargs={'pk': self.kwargs['pk']})

# User Profile
class UserProfileView(LoginRequiredMixin, View):
    template_name = 'store/profile.html'

    def get(self, request):
        user_profile, created = UserProfile.objects.get_or_create(user=request.user)
        info_form = UserInfoForm(instance=user_profile)
        profile_form = UserProfileForm(instance=user_profile)
        password_form = UserPasswordChangeForm(user=request.user)
        return render(request, self.template_name, {
            'info_form': info_form,
            'profile_form': profile_form,
            'password_form': password_form,
        })

    def post(self, request):
        user_profile, created = UserProfile.objects.get_or_create(user=request.user)
        if 'update_profile' in request.POST:
            profile_form = UserProfileForm(request.POST, request.FILES, instance=user_profile)
            if profile_form.is_valid():
                profile_form.save()
                messages.success(request, "Profile updated successfully.")
                return redirect('user_profile')
            else:
                messages.error(request, "Failed to update profile. Please check the form.")
                return render(request, self.template_name, {
                    'info_form': UserInfoForm(instance=user_profile),
                    'profile_form': profile_form,
                    'password_form': UserPasswordChangeForm(user=request.user),
                })
        elif 'change_password' in request.POST:
            password_form = UserPasswordChangeForm(request.POST, user=request.user)
            if password_form.is_valid():
                request.user.set_password(password_form.cleaned_data['new_password'])
                request.user.save()
                messages.success(request, "Password changed successfully. Please log in again.")
                return redirect('login')
            else:
                messages.error(request, "Failed to change password. Please check the form.")
                return render(request, self.template_name, {
                    'info_form': UserInfoForm(instance=user_profile),
                    'profile_form': UserProfileForm(instance=user_profile),
                    'password_form': password_form,
                })
        return redirect('user_profile')

# Notification Management
class NotificationView(LoginRequiredMixin, ListView):
    template_name = 'store/notifications.html'
    context_object_name = 'notifications'
    paginate_by = 10

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user).select_related('order').order_by('-created_at')

    def post(self, request):
        notification_id = request.POST.get('notification_id')
        if notification_id:
            notification = get_object_or_404(Notification, id=notification_id, user=request.user)
            notification.is_read = True
            notification.save()
            messages.success(request, "Notification marked as read.")
        return redirect('notifications')

# Authentication Views
class CustomLoginView(LoginView):
    template_name = 'store/login.html'
    redirect_authenticated_user = True

    def form_valid(self, form):
        messages.success(self.request, "Logged in successfully.")
        return super().form_valid(form)

class CustomLogoutView(LogoutView):
    next_page = reverse_lazy('user_dashboard')

    def dispatch(self, request, *args, **kwargs):
        messages.success(request, "Logged out successfully.")
        return super().dispatch(request, *args, **kwargs)

class RegisterView(CreateView):
    form_class = RegisterForm
    template_name = 'store/register.html'
    success_url = reverse_lazy('user_dashboard')

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            messages.warning(request, "You are already logged in.")
            return redirect('user_dashboard')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        with transaction.atomic():
            response = super().form_valid(form)
            user = form.save()  # RegisterForm creates UserProfile
            Customer.objects.get_or_create(user=user)
            messages.success(self.request, "Registration successful! Please log in.")
            return response