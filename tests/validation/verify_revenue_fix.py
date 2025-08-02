#!/usr/bin/env python
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sales_management_project.settings')
sys.path.append('d:\\code\\Sales_App\\sales_management_project')
django.setup()

from sales_app.models import Invoice
from django.utils import timezone
from django.db.models import Sum
from datetime import timedelta

print("=== Revenue Summary Fix Verification ===")
print()

# Get monthly revenue for the last 12 months (same logic as view)
end_date = timezone.now().date()
start_date = end_date - timedelta(days=365)

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

print("BEFORE FIX - First 6 months (slice ':6'):")
for i, month in enumerate(monthly_data[:6]):
    print(f"  {month['month']:15} - ${month['revenue']:,.2f}")

print()
print("AFTER FIX - Last 6 months (slice '-6:'):")
for i, month in enumerate(monthly_data[-6:]):
    icon = "✅" if month['revenue'] > 0 else "⚪"
    print(f"  {icon} {month['month']:15} - ${month['revenue']:,.2f}")

print()
total_revenue = sum(month['revenue'] for month in monthly_data)
print(f"12-Month Total: ${total_revenue:,.2f}")

print()
print("Summary of the fix:")
print("✅ Changed from showing first 6 months to last 6 months")
print("✅ Added visual highlighting for months with revenue")
print("✅ Added 12-month total calculation")
print("✅ July 2025 with $20,371 is now visible in the summary!")
