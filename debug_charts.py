#!/usr/bin/env python
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sales_management_project.settings')
sys.path.append('d:\\code\\Sales_App\\sales_management_project')
django.setup()

from sales_app.models import Invoice
from accounting_app.models import Expense
from django.utils import timezone
from django.db.models import Sum, Count
from datetime import timedelta

print("=== Chart Data Debug ===")
print()

# Check revenue data (for revenue tracking chart)
end_date = timezone.now().date()
start_date = end_date - timedelta(days=365)

print(f"Date range: {start_date} to {end_date}")
print()

monthly_data = []
for i in range(12):
    month_start = (start_date.replace(day=1) + timedelta(days=32*i)).replace(day=1)
    month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
    
    if month_end > end_date:
        month_end = end_date
    
    revenue = Invoice.objects.filter(
        date_of_sale__range=[month_start, month_end]
    ).aggregate(total=Sum('total'))['total'] or 0
    
    monthly_data.append({
        'month': month_start.strftime('%B %Y'),
        'revenue': float(revenue),
        'month_start': month_start,
        'month_end': month_end
    })
    
    print(f"{month_start.strftime('%B %Y')}: ${revenue}")

print()
print("Monthly data for chart:")
print("Labels:", [month['month'] for month in monthly_data])
print("Data:", [month['revenue'] for month in monthly_data])

print()
print("=== Expense Data (for P&L chart) ===")

# Check expense data (for profit & loss chart)
expense_data = Expense.objects.values('category__name').annotate(
    total=Sum('amount'),
    count=Count('id')
).order_by('-total')

for expense in expense_data:
    print(f"{expense['category__name']}: ${expense['total']} ({expense['count']} items)")

print()
print("Expense data for chart:")
print("Labels:", [expense['category__name'] for expense in expense_data])
print("Data:", [float(expense['total']) for expense in expense_data])
