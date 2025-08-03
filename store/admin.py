from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline
from django.http import HttpResponse
import csv
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from .models import (
    Category, Product, FarmingProduct, Farm, BusinessLocation, UserProfile, Customer,
    Order, OrderItem, DeliveryTracking, SalesRecord, AnnualProduction, ProfitLoss,
    PaymentTransaction, Review, Tax, Discount, Notification, AuditLog, FarmTool,
    ToolMaintenance, Management, Staff, StaffSalary, StaffPerformance, StaffPromotion,
    RelationshipRecord, Supplier, Inventory, Contract, Expense, Report, ReportExport
)

# Generic Inline for ReportExport
class ReportExportInline(GenericTabularInline):
    model = ReportExport
    extra = 1
    fields = ['title', 'export_format', 'status', 'file', 'created_at']
    readonly_fields = ['created_at', 'file']

# Export action mixin for CSV/PDF
class ExportReportMixin:
    def export_as_csv(self, request, queryset):
        meta = self.model._meta
        field_names = [field.name for field in meta.fields]
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename={meta}.csv'
        writer = csv.writer(response)
        writer.writerow(field_names)
        for obj in queryset:
            writer.writerow([getattr(obj, field) for field in field_names])
        return response

    def export_as_pdf(self, request, queryset):
        meta = self.model._meta
        field_names = [field.name for field in meta.fields]
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename={meta}.pdf'
        p = canvas.Canvas(response, pagesize=letter)
        y = 750
        p.drawString(100, y, f"{meta.verbose_name_plural} Report")
        y -= 30
        p.drawString(100, y, ", ".join(field_names))
        y -= 20
        for obj in queryset:
            row = ", ".join([str(getattr(obj, field)) for field in field_names])
            p.drawString(100, y, row)
            y -= 20
            if y < 50:
                p.showPage()
                y = 750
        p.showPage()
        p.save()
        return response

    export_as_csv.short_description = "Export selected as CSV"
    export_as_pdf.short_description = "Export selected as PDF"

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price', 'stock', 'is_active', 'created_at']
    list_filter = ['category', 'is_active']
    search_fields = ['name', 'description']
    inlines = [ReportExportInline]

@admin.register(FarmingProduct)
class FarmingProductAdmin(admin.ModelAdmin):
    list_display = ['product', 'crop_type', 'farm', 'organic', 'created_at']
    list_filter = ['organic', 'farm']
    search_fields = ['product__name', 'crop_type']
    inlines = [ReportExportInline]

@admin.register(Farm)
class FarmAdmin(admin.ModelAdmin):
    list_display = ['name', 'location', 'farm_type', 'size_hectares', 'is_active']
    list_filter = ['farm_type', 'is_active']
    search_fields = ['name', 'location__name']
    inlines = [ReportExportInline]

@admin.register(BusinessLocation)
class BusinessLocationAdmin(admin.ModelAdmin):
    list_display = ['name', 'city', 'country', 'is_active']
    list_filter = ['country', 'is_active']
    search_fields = ['name', 'city', 'country']
    inlines = [ReportExportInline]

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone', 'city', 'country', 'is_verified']
    list_filter = ['is_verified', 'country']
    search_fields = ['user__username', 'phone', 'address']
    inlines = [ReportExportInline]

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['user', 'loyalty_points', 'last_purchase']
    search_fields = ['user__username', 'preferred_payment_method']
    inlines = [ReportExportInline]

@admin.register(Order)
class OrderAdmin(ExportReportMixin, admin.ModelAdmin):
    list_display = ['id', 'user', 'total_price', 'status', 'ordered_at']
    list_filter = ['status', 'ordered_at']
    search_fields = ['user__username', 'shipping_address']
    actions = ['export_as_csv', 'export_as_pdf']
    inlines = [ReportExportInline]

@admin.register(OrderItem)
class OrderItemAdmin(ExportReportMixin, admin.ModelAdmin):
    list_display = ['order', 'product', 'quantity', 'subtotal']
    search_fields = ['product__name']
    actions = ['export_as_csv', 'export_as_pdf']
    inlines = [ReportExportInline]

@admin.register(DeliveryTracking)
class DeliveryTrackingAdmin(ExportReportMixin, admin.ModelAdmin):
    list_display = ['order', 'tracking_number', 'status', 'last_updated']
    list_filter = ['status']
    search_fields = ['tracking_number', 'carrier']
    actions = ['export_as_csv', 'export_as_pdf']
    inlines = [ReportExportInline]

@admin.register(SalesRecord)
class SalesRecordAdmin(ExportReportMixin, admin.ModelAdmin):
    list_display = ['product', 'quantity_sold', 'sale_price', 'sale_date']
    list_filter = ['sale_date', 'location']
    search_fields = ['product__name']
    actions = ['export_as_csv', 'export_as_pdf']
    inlines = [ReportExportInline]

@admin.register(AnnualProduction)
class AnnualProductionAdmin(ExportReportMixin, admin.ModelAdmin):
    list_display = ['farm', 'product', 'year', 'quantity_produced', 'unit', 'revenue']
    list_filter = ['year', 'farm']
    search_fields = ['product__product__name']
    actions = ['export_as_csv', 'export_as_pdf']
    inlines = [ReportExportInline]

@admin.register(ProfitLoss)
class ProfitLossAdmin(ExportReportMixin, admin.ModelAdmin):
    list_display = ['product', 'order', 'revenue', 'cost', 'profit', 'period_start']
    list_filter = ['period_start', 'period_end']
    search_fields = ['product__name']
    actions = ['export_as_csv', 'export_as_pdf']
    inlines = [ReportExportInline]

@admin.register(PaymentTransaction)
class PaymentTransactionAdmin(ExportReportMixin, admin.ModelAdmin):
    list_display = ['transaction_id', 'order', 'amount', 'status', 'gateway', 'created_at']
    list_filter = ['status', 'gateway']
    search_fields = ['transaction_id', 'order__id']
    actions = ['export_as_csv', 'export_as_pdf']
    inlines = [ReportExportInline]

@admin.register(Review)
class ReviewAdmin(ExportReportMixin, admin.ModelAdmin):
    list_display = ['product', 'user', 'rating', 'is_approved', 'created_at']
    list_filter = ['is_approved', 'rating']
    search_fields = ['product__name', 'user__username']
    actions = ['export_as_csv', 'export_as_pdf']
    inlines = [ReportExportInline]

@admin.register(Tax)
class TaxAdmin(admin.ModelAdmin):
    list_display = ['name', 'country', 'rate', 'is_active']
    list_filter = ['country', 'is_active']
    search_fields = ['name', 'country']
    inlines = [ReportExportInline]

@admin.register(Discount)
class DiscountAdmin(admin.ModelAdmin):
    list_display = ['code', 'discount_type', 'value', 'is_active', 'start_date', 'end_date']
    list_filter = ['is_active', 'discount_type']
    search_fields = ['code', 'description']
    inlines = [ReportExportInline]

@admin.register(Notification)
class NotificationAdmin(ExportReportMixin, admin.ModelAdmin):
    list_display = ['user', 'type', 'is_read', 'created_at']
    list_filter = ['type', 'is_read']
    search_fields = ['user__username', 'message']
    actions = ['export_as_csv', 'export_as_pdf']
    inlines = [ReportExportInline]

@admin.register(AuditLog)
class AuditLogAdmin(ExportReportMixin, admin.ModelAdmin):
    list_display = ['action', 'user', 'model_name', 'object_id', 'timestamp']
    list_filter = ['model_name', 'timestamp']
    search_fields = ['action', 'user__username', 'details']
    actions = ['export_as_csv', 'export_as_pdf']
    inlines = [ReportExportInline]

@admin.register(FarmTool)
class FarmToolAdmin(admin.ModelAdmin):
    list_display = ['name', 'tool_type', 'location', 'is_operational', 'created_at']
    list_filter = ['tool_type', 'is_operational']
    search_fields = ['name', 'serial_number']
    inlines = [ReportExportInline]

@admin.register(ToolMaintenance)
class ToolMaintenanceAdmin(ExportReportMixin, admin.ModelAdmin):
    list_display = ['farm_tool', 'maintenance_date', 'cost', 'performed_by']
    list_filter = ['maintenance_date']
    search_fields = ['farm_tool__name', 'description']
    actions = ['export_as_csv', 'export_as_pdf']
    inlines = [ReportExportInline]

@admin.register(Management)
class ManagementAdmin(admin.ModelAdmin):
    list_display = ['user', 'role', 'department', 'location', 'is_active']
    list_filter = ['role', 'is_active']
    search_fields = ['user__username', 'department']
    inlines = [ReportExportInline]

@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):
    list_display = ['user', 'job_title', 'location', 'hire_date', 'is_active']
    list_filter = ['is_active', 'location']
    search_fields = ['user__username', 'job_title']
    inlines = [ReportExportInline]

@admin.register(StaffSalary)
class StaffSalaryAdmin(ExportReportMixin, admin.ModelAdmin):
    list_display = ['staff', 'base_salary', 'net_salary', 'payment_date', 'status']
    list_filter = ['status', 'payment_frequency']
    search_fields = ['staff__user__username']
    actions = ['export_as_csv', 'export_as_pdf']
    inlines = [ReportExportInline]

@admin.register(StaffPerformance)
class StaffPerformanceAdmin(ExportReportMixin, admin.ModelAdmin):
    list_display = ['staff', 'performance_score', 'evaluation_date', 'evaluated_by']
    list_filter = ['evaluation_date']
    search_fields = ['staff__user__username', 'metrics']
    actions = ['export_as_csv', 'export_as_pdf']
    inlines = [ReportExportInline]

@admin.register(StaffPromotion)
class StaffPromotionAdmin(ExportReportMixin, admin.ModelAdmin):
    list_display = ['staff', 'new_role', 'promotion_date', 'approved_by']
    list_filter = ['promotion_date']
    search_fields = ['staff__user__username', 'new_role']
    actions = ['export_as_csv', 'export_as_pdf']
    inlines = [ReportExportInline]

@admin.register(RelationshipRecord)
class RelationshipRecordAdmin(ExportReportMixin, admin.ModelAdmin):
    list_display = ['relationship_type', 'primary_entity', 'secondary_entity', 'start_date']
    list_filter = ['relationship_type']
    search_fields = ['primary_entity', 'secondary_entity']
    actions = ['export_as_csv', 'export_as_pdf']
    inlines = [ReportExportInline]

@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ['name', 'contact_person', 'phone', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name', 'contact_person', 'email']
    inlines = [ReportExportInline]

@admin.register(Inventory)
class InventoryAdmin(ExportReportMixin, admin.ModelAdmin):
    list_display = ['product', 'farm_tool', 'location', 'quantity', 'unit']
    list_filter = ['location']
    search_fields = ['product__name', 'farm_tool__name']
    actions = ['export_as_csv', 'export_as_pdf']
    inlines = [ReportExportInline]

@admin.register(Contract)
class ContractAdmin(ExportReportMixin, admin.ModelAdmin):
    list_display = ['title', 'contract_type', 'start_date', 'is_active']
    list_filter = ['contract_type', 'is_active']
    search_fields = ['title', 'description']
    actions = ['export_as_csv', 'export_as_pdf']
    inlines = [ReportExportInline]

@admin.register(Expense)
class ExpenseAdmin(ExportReportMixin, admin.ModelAdmin):
    list_display = ['description', 'expense_type', 'amount', 'date_incurred']
    list_filter = ['expense_type', 'date_incurred']
    search_fields = ['description']
    actions = ['export_as_csv', 'export_as_pdf']
    inlines = [ReportExportInline]

@admin.register(Report)
class ReportAdmin(ExportReportMixin, admin.ModelAdmin):
    list_display = ['title', 'report_type', 'generated_at', 'generated_by']
    list_filter = ['report_type', 'generated_at']
    search_fields = ['title']
    actions = ['export_as_csv', 'export_as_pdf']
    inlines = [ReportExportInline]

@admin.register(ReportExport)
class ReportExportAdmin(admin.ModelAdmin):
    list_display = ['title', 'export_format', 'status', 'created_at', 'user']
    list_filter = ['export_format', 'status']
    search_fields = ['title', 'user__username']
    readonly_fields = ['file', 'created_at', 'updated_at']
