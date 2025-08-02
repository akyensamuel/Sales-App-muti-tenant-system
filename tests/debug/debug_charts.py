#!/usr/bin/env python
import os
import sys
from pathlib import Path

# Add tests directory to path and setup Django
sys.path.insert(0, str(Path(__file__).parent.parent))
from django_setup import setup_django
setup_django()

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
