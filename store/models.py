from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from decimal import Decimal

# Category for organizing products
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    slug = models.SlugField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name

# Product details (general products, including non-agricultural)
class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='products')
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    stock = models.PositiveIntegerField()
    image = models.ImageField(upload_to='products/', null=True, blank=True)
    weight = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['name', 'category']),
        ]

    def __str__(self):
        return self.name

# Farming Product (specific to agricultural produce)
class FarmingProduct(models.Model):
    product = models.OneToOneField(Product, on_delete=models.CASCADE, related_name='farming_product')
    crop_type = models.CharField(max_length=100, blank=True)
    harvest_date = models.DateField(null=True, blank=True)
    farm = models.ForeignKey('Farm', on_delete=models.SET_NULL, null=True, related_name='farming_products')
    organic = models.BooleanField(default=False)
    certification = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.product.name} (Farming Product)"

# Business Location (e.g., warehouse, farm, store)
class BusinessLocation(models.Model):
    name = models.CharField(max_length=100)
    address = models.TextField()
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.city}, {self.country}"

# Farm (individual farming sites)
class Farm(models.Model):
    name = models.CharField(max_length=100)
    location = models.ForeignKey(BusinessLocation, on_delete=models.SET_NULL, null=True, related_name='farms')
    size_hectares = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    farm_type = models.CharField(max_length=50, choices=[
        ('crop', 'Crop'),
        ('livestock', 'Livestock'),
        ('mixed', 'Mixed'),
    ])
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='farms')
    established_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.farm_type})"

# User Profile for extended user information
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    profile_picture = models.ImageField(upload_to='profiles/', null=True, blank=True)
    is_verified = models.BooleanField(default=False)
    preferred_currency = models.CharField(max_length=3, default='USD')
    bio = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username

# Customer (extends user profile for buyer-specific data)
class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='customer_profile')
    loyalty_points = models.PositiveIntegerField(default=0)
    last_purchase = models.DateTimeField(null=True, blank=True)
    preferred_payment_method = models.CharField(max_length=50, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Customer: {self.user.username}"

# Order details
class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    location = models.ForeignKey(BusinessLocation, on_delete=models.SET_NULL, null=True, related_name='orders')
    total_price = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    shipping_address = models.TextField()
    shipping_city = models.CharField(max_length=100)
    shipping_country = models.CharField(max_length=100)
    shipping_postal_code = models.CharField(max_length=20, blank=True)
    ordered_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['user', 'status', 'ordered_at']),
        ]

    def __str__(self):
        return f"Order {self.id} by {self.user.username}"

# Order Item (products within an order)
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, related_name='order_items')
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))

    def save(self, *args, **kwargs):
        self.subtotal = Decimal(str(self.unit_price)) * Decimal(str(self.quantity))
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.quantity} x {self.product.name} (Order {self.order.id})"

# Delivery Tracking
class DeliveryTracking(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='delivery')
    tracking_number = models.CharField(max_length=50, unique=True, blank=True)
    carrier = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=50, choices=[
        ('preparing', 'Preparing'),
        ('in_transit', 'In Transit'),
        ('out_for_delivery', 'Out for Delivery'),
        ('delivered', 'Delivered'),
        ('failed', 'Failed'),
    ], default='preparing')
    estimated_delivery = models.DateTimeField(null=True, blank=True)
    last_updated = models.DateTimeField(auto_now=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"Tracking for Order {self.order.id}"

# Sales Record
class SalesRecord(models.Model):
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, related_name='sales')
    order_item = models.ForeignKey(OrderItem, on_delete=models.CASCADE, related_name='sales_records')
    quantity_sold = models.PositiveIntegerField()
    sale_price = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    sale_date = models.DateTimeField(default=timezone.now)
    location = models.ForeignKey(BusinessLocation, on_delete=models.SET_NULL, null=True, related_name='sales')

    def __str__(self):
        return f"Sale of {self.quantity_sold} x {self.product.name} on {self.sale_date}"

# Annual Production (yearly farm output)
class AnnualProduction(models.Model):
    farm = models.ForeignKey(Farm, on_delete=models.CASCADE, related_name='productions')
    product = models.ForeignKey(FarmingProduct, on_delete=models.SET_NULL, null=True, related_name='productions')
    year = models.PositiveIntegerField()
    quantity_produced = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    unit = models.CharField(max_length=50)
    revenue = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    cost = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['farm', 'product', 'year']
        indexes = [
            models.Index(fields=['year', 'farm']),
        ]

    def __str__(self):
        return f"{self.product.product.name} ({self.quantity_produced} {self.unit}) in {self.year}"

# Profit and Loss
class ProfitLoss(models.Model):
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, related_name='profit_loss')
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, related_name='profit_loss')
    revenue = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    cost = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    profit = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    period_start = models.DateTimeField()
    period_end = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        self.profit = Decimal(str(self.revenue)) - Decimal(str(self.cost))
        super().save(*args, **kwargs)

    def __str__(self):
        return f"P&L for {self.product or 'Order'} ({self.period_start} to {self.period_end})"

# Payment Transaction
class PaymentTransaction(models.Model):
    PAYMENT_STATUS = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]

    GATEWAY_CHOICES = [
        ('stripe', 'Stripe'),
        ('paypal', 'PayPal'),
        ('bank_transfer', 'Bank Transfer'),
    ]

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='payments')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    currency = models.CharField(max_length=3, default='USD')
    gateway = models.CharField(max_length=20, choices=GATEWAY_CHOICES)
    transaction_id = models.CharField(max_length=100, unique=True)
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['transaction_id', 'status']),
        ]

    def __str__(self):
        return f"Payment {self.transaction_id} for Order {self.order.id}"

# Product Review
class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveSmallIntegerField(choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_approved = models.BooleanField(default=False)

    class Meta:
        unique_together = ['product', 'user']

    def __str__(self):
        return f"{self.rating} stars for {self.product.name} by {self.user.username}"

# Tax Configuration
class Tax(models.Model):
    country = models.CharField(max_length=100)
    rate = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0.00'))
    name = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.rate}%) - {self.country}"

# Discount/Promotion
class Discount(models.Model):
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True)
    discount_type = models.CharField(max_length=20, choices=[
        ('percentage', 'Percentage'),
        ('fixed', 'Fixed Amount'),
    ])
    value = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    max_uses = models.PositiveIntegerField(null=True, blank=True)
    used_count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.code} ({self.discount_type}: {self.value})"

# Notification
class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, blank=True, related_name='notifications')
    type = models.CharField(max_length=50, choices=[
        ('order_update', 'Order Update'),
        ('promotion', 'Promotion'),
        ('system', 'System'),
    ])

    def __str__(self):
        return f"Notification for {self.user.username}: {self.message[:50]}"

# Audit Log for security and compliance
class AuditLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='audit_logs')
    action = models.CharField(max_length=100)
    model_name = models.CharField(max_length=100, blank=True)
    object_id = models.CharField(max_length=50, blank=True)
    details = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    def __str__(self):
        return f"{self.action} by {self.user or 'Anonymous'} at {self.timestamp}"

# Farm Tool (machines and equipment)
class FarmTool(models.Model):
    TOOL_TYPE_CHOICES = [
        ('tractor', 'Tractor'),
        ('plow', 'Plow'),
        ('harvester', 'Harvester'),
        ('irrigation', 'Irrigation System'),
        ('other', 'Other'),
    ]

    name = models.CharField(max_length=100)
    tool_type = models.CharField(max_length=50, choices=TOOL_TYPE_CHOICES)
    description = models.TextField(blank=True)
    serial_number = models.CharField(max_length=50, unique=True, blank=True)
    location = models.ForeignKey(BusinessLocation, on_delete=models.SET_NULL, null=True, related_name='farm_tools')
    purchase_date = models.DateField(null=True, blank=True)
    cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    is_operational = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['serial_number', 'tool_type']),
        ]

    def __str__(self):
        return f"{self.name} ({self.tool_type})"

# Farm Tool Maintenance Record
class ToolMaintenance(models.Model):
    farm_tool = models.ForeignKey(FarmTool, on_delete=models.CASCADE, related_name='maintenance_records')
    maintenance_date = models.DateTimeField()
    description = models.TextField()
    cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    performed_by = models.CharField(max_length=100, blank=True)
    next_maintenance = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Maintenance for {self.farm_tool.name} on {self.maintenance_date}"

# Management (hierarchy and roles)
class Management(models.Model):
    ROLE_CHOICES = [
        ('executive', 'Executive'),
        ('manager', 'Manager'),
        ('supervisor', 'Supervisor'),
        ('administrator', 'Administrator'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='management_roles')
    role = models.CharField(max_length=50, choices=ROLE_CHOICES)
    department = models.CharField(max_length=100, blank=True)
    location = models.ForeignKey(BusinessLocation, on_delete=models.SET_NULL, null=True, related_name='managers')
    start_date = models.DateField()
    is_active = models.BooleanField(default=True)
    responsibilities = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['user', 'role', 'location']
        indexes = [
            models.Index(fields=['role', 'is_active']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.role} at {self.location}"

# Staff (employee details)
class Staff(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='staff_profile')
    date_of_birth = models.DateField()
    state = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100)
    address = models.TextField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    certification = models.TextField(blank=True)
    hire_date = models.DateField()
    job_title = models.CharField(max_length=100)
    location = models.ForeignKey(BusinessLocation, on_delete=models.SET_NULL, null=True, related_name='staff')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['job_title', 'is_active']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.job_title}"

# Staff Salary
class StaffSalary(models.Model):
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE, related_name='salaries')
    base_salary = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    currency = models.CharField(max_length=3, default='USD')
    payment_frequency = models.CharField(max_length=20, choices=[
        ('monthly', 'Monthly'),
        ('biweekly', 'Biweekly'),
        ('weekly', 'Weekly'),
    ])
    deductions = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    net_salary = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    payment_date = models.DateField()
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('delayed', 'Delayed'),
    ], default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        self.net_salary = Decimal(str(self.base_salary)) - Decimal(str(self.deductions))
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Salary for {self.staff.user.username} on {self.payment_date}"

# Staff Performance
class StaffPerformance(models.Model):
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE, related_name='performance_records')
    evaluation_date = models.DateTimeField()
    performance_score = models.PositiveSmallIntegerField(choices=[(i, i) for i in range(1, 11)])
    metrics = models.TextField()
    comments = models.TextField(blank=True)
    evaluated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='evaluations_conducted')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Performance of {self.staff.user.username} on {self.evaluation_date}"

# Staff Promotion
class StaffPromotion(models.Model):
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE, related_name='promotions')
    previous_role = models.CharField(max_length=100)
    new_role = models.CharField(max_length=100)
    promotion_date = models.DateField()
    salary_change = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    reason = models.TextField(blank=True)
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='promotions_approved')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Promotion of {self.staff.user.username} to {self.new_role} on {self.promotion_date}"

# Relationship Record (e.g., staff to manager, farm to supplier)
class RelationshipRecord(models.Model):
    RELATIONSHIP_TYPE_CHOICES = [
        ('staff_manager', 'Staff-Manager'),
        ('farm_supplier', 'Farm-Supplier'),
        ('farm_location', 'Farm-Location'),
        ('staff_farm', 'Staff-Farm'),
    ]

    relationship_type = models.CharField(max_length=50, choices=RELATIONSHIP_TYPE_CHOICES)
    primary_entity = models.CharField(max_length=100)
    secondary_entity = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['relationship_type', 'primary_entity', 'secondary_entity']
        indexes = [
            models.Index(fields=['relationship_type', 'primary_entity']),
        ]

    def __str__(self):
        return f"{self.relationship_type}: {self.primary_entity} -> {self.secondary_entity}"

# Supplier (for tools, seeds, etc.)
class Supplier(models.Model):
    name = models.CharField(max_length=100)
    contact_person = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

# Inventory (for farming products and tools)
class Inventory(models.Model):
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, related_name='inventory')
    farm_tool = models.ForeignKey(FarmTool, on_delete=models.SET_NULL, null=True, related_name='inventory')
    location = models.ForeignKey(BusinessLocation, on_delete=models.SET_NULL, null=True, related_name='inventory')
    quantity = models.PositiveIntegerField()
    unit = models.CharField(max_length=50, blank=True)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['product', 'farm_tool', 'location']
        indexes = [
            models.Index(fields=['location', 'product']),
        ]

    def __str__(self):
        item = self.product or self.farm_tool
        return f"{item} at {self.location} ({self.quantity} {self.unit})"

# Contract (e.g., supplier agreements, staff contracts)
class Contract(models.Model):
    CONTRACT_TYPE_CHOICES = [
        ('supplier', 'Supplier'),
        ('staff', 'Staff'),
        ('buyer', 'Buyer'),
    ]

    contract_type = models.CharField(max_length=50, choices=CONTRACT_TYPE_CHOICES)
    title = models.CharField(max_length=200)
    description = models.TextField()
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    party = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='contracts')
    supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True, related_name='contracts')
    value = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.contract_type}: {self.title}"

# Expense (operational costs)
class Expense(models.Model):
    EXPENSE_TYPE_CHOICES = [
        ('utilities', 'Utilities'),
        ('transport', 'Transport'),
        ('maintenance', 'Maintenance'),
        ('salaries', 'Salaries'),
        ('other', 'Other'),
    ]

    description = models.CharField(max_length=200)
    expense_type = models.CharField(max_length=50, choices=EXPENSE_TYPE_CHOICES)
    amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    currency = models.CharField(max_length=3, default='USD')
    date_incurred = models.DateField()
    location = models.ForeignKey(BusinessLocation, on_delete=models.SET_NULL, null=True, related_name='expenses')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.expense_type}: {self.amount} on {self.date_incurred}"

# Report (generated reports for analytics)
class Report(models.Model):
    REPORT_TYPE_CHOICES = [
        ('sales', 'Sales'),
        ('production', 'Production'),
        ('profit_loss', 'Profit & Loss'),
        ('staff_performance', 'Staff Performance'),
    ]

    report_type = models.CharField(max_length=50, choices=REPORT_TYPE_CHOICES)
    title = models.CharField(max_length=200)
    data = models.JSONField()
    generated_at = models.DateTimeField(auto_now_add=True)
    generated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='reports')
    period_start = models.DateTimeField()
    period_end = models.DateTimeField()

    def __str__(self):
        return f"{self.report_type}: {self.title} ({self.period_start} to {self.period_end})"

# Report Export (for CSV/PDF exports of record-tracking models)
class ReportExport(models.Model):
    EXPORT_FORMAT_CHOICES = [
        ('csv', 'CSV'),
        ('pdf', 'PDF'),
    ]

    EXPORT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.CharField(max_length=50)
    content_object = GenericForeignKey('content_type', 'object_id')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='report_exports')
    export_format = models.CharField(max_length=10, choices=EXPORT_FORMAT_CHOICES)
    status = models.CharField(max_length=20, choices=EXPORT_STATUS_CHOICES, default='pending')
    file = models.FileField(upload_to='reports/', null=True, blank=True)
    title = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['content_type', 'object_id', 'status']),
        ]

    def __str__(self):
        return f"{self.title} ({self.export_format}) - {self.status}"

class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cart')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'product']

    def __str__(self):
        return f"{self.user.username}'s cart: {self.product.name} x {self.quantity}"