from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal

class ExpenseCategory(models.Model):
    """Categories for organizing expenses"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = "Expense Categories"
        ordering = ['name']
    
    def __str__(self):
        return self.name

class Expense(models.Model):
    """Record business expenses"""
    PAYMENT_METHODS = [
        ('cash', 'Cash'),
        ('card', 'Credit/Debit Card'),
        ('bank', 'Bank Transfer'),
        ('cheque', 'Cheque'),
        ('other', 'Other'),
    ]
    
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    date = models.DateField(default=timezone.now)
    category = models.ForeignKey(ExpenseCategory, on_delete=models.CASCADE, related_name='expenses')
    description = models.CharField(max_length=255)
    notes = models.TextField(blank=True)
    payment_method = models.CharField(max_length=10, choices=PAYMENT_METHODS, default='cash')
    receipt_file = models.FileField(upload_to='receipts/%Y/%m/', blank=True, null=True)
    vendor = models.CharField(max_length=100, blank=True)
    reference_number = models.CharField(max_length=50, blank=True)
    is_recurring = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-date', '-created_at']
    
    def __str__(self):
        return f"{self.category.name} - ${self.amount} on {self.date}"

class ProfitLossSnapshot(models.Model):
    """Monthly P&L snapshots for performance tracking"""
    month = models.DateField()  # First day of the month
    total_revenue = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total_expenses = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    net_profit = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total_invoices = models.IntegerField(default=0)
    paid_invoices = models.IntegerField(default=0)
    unpaid_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['month']
        ordering = ['-month']
    
    def __str__(self):
        return f"P&L for {self.month.strftime('%B %Y')}"
    
    @property
    def profit_margin(self):
        """Calculate profit margin percentage"""
        if self.total_revenue > 0:
            return (self.net_profit / self.total_revenue) * 100
        return 0

class TaxSettings(models.Model):
    """Tax configuration for automatic calculations"""
    vat_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.00, help_text="VAT rate in percentage")
    income_tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.00, help_text="Income tax rate in percentage")
    tax_year_start = models.DateField(default=timezone.now)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = "Tax Settings"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Tax Config: VAT {self.vat_rate}%, Income Tax {self.income_tax_rate}%"

class AccountingAuditLog(models.Model):
    """Audit trail for all accounting operations"""
    ACTION_CHOICES = [
        ('create', 'Created'),
        ('update', 'Updated'),
        ('delete', 'Deleted'),
        ('view', 'Viewed'),
        ('export', 'Exported'),
        ('import', 'Imported'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    action = models.CharField(max_length=10, choices=ACTION_CHOICES)
    model_name = models.CharField(max_length=50)
    object_id = models.CharField(max_length=50, blank=True)
    details = models.TextField()
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.user.username} {self.action} {self.model_name} at {self.timestamp}"

class FinancialForecast(models.Model):
    """Financial forecasting for business planning"""
    job_type = models.CharField(max_length=100)
    projected_revenue = models.DecimalField(max_digits=12, decimal_places=2)
    forecast_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.job_type} - {self.forecast_date}"