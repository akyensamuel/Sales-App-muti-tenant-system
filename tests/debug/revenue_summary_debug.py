#!/usr/bin/env python
import os
import sys
from pathlib import Path

# Add tests directory to path and setup Django
sys.path.insert(0, str(Path(__file__).parent.parent))
from django_setup import setup_django
setup_django()

from sales_app.models import Invoice
from django.utils import timezone
from django.db.models import Sum
from datetime import timedelta

print("=== Revenue Summary Analysis ===")
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

print("All 12 months of data:")
for i, month in enumerate(monthly_data):
    print(f"{i+1:2d}. {month['month']:15} - ${month['revenue']:,.2f}")

print()
print("First 6 months (displayed in Revenue Summary):")
for i, month in enumerate(monthly_data[:6]):
    print(f"{i+1:2d}. {month['month']:15} - ${month['revenue']:,.2f}")

print()
print("Last 6 months:")
for i, month in enumerate(monthly_data[6:], 7):
    print(f"{i:2d}. {month['month']:15} - ${month['revenue']:,.2f}")

# Check total revenue
total_revenue = sum(month['revenue'] for month in monthly_data)
print(f"\nTotal Revenue (12 months): ${total_revenue:,.2f}")
print(f"Average Monthly Revenue: ${total_revenue/12:,.2f}")

# Check which months have actual data
months_with_revenue = [month for month in monthly_data if month['revenue'] > 0]
print(f"\nMonths with revenue ({len(months_with_revenue)}):")
for month in months_with_revenue:
    print(f"  {month['month']:15} - ${month['revenue']:,.2f}")
