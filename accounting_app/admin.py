from django.contrib import admin
from .models import (
    ExpenseCategory, Expense, ProfitLossSnapshot, 
    TaxSettings, AccountingAuditLog, FinancialForecast
)

@admin.register(ExpenseCategory)
class ExpenseCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name', 'description']

@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ['description', 'amount', 'category', 'date', 'payment_method', 'created_by']
    list_filter = ['category', 'payment_method', 'date', 'is_recurring']
    search_fields = ['description', 'vendor', 'reference_number']
    date_hierarchy = 'date'
    readonly_fields = ['created_at', 'updated_at']
    
    def save_model(self, request, obj, form, change):
        if not change:  # Only set created_by for new objects
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

@admin.register(ProfitLossSnapshot)
class ProfitLossSnapshotAdmin(admin.ModelAdmin):
    list_display = ['month', 'total_revenue', 'total_expenses', 'net_profit', 'profit_margin']
    list_filter = ['month']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(TaxSettings)
class TaxSettingsAdmin(admin.ModelAdmin):
    list_display = ['vat_rate', 'income_tax_rate', 'tax_year_start', 'is_active']
    list_filter = ['is_active', 'tax_year_start']

@admin.register(AccountingAuditLog)
class AccountingAuditLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'action', 'model_name', 'timestamp']
    list_filter = ['action', 'model_name', 'timestamp']
    search_fields = ['user__username', 'details']
    readonly_fields = ['timestamp']

@admin.register(FinancialForecast)
class FinancialForecastAdmin(admin.ModelAdmin):
    list_display = ['job_type', 'projected_revenue', 'forecast_date', 'created_at']
    list_filter = ['forecast_date', 'created_at']
    search_fields = ['job_type']
