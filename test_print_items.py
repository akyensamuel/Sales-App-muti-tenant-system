#!/usr/bin/env python
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sales_management_project.settings')
sys.path.append('d:\\code\\Sales_App\\sales_management_project')
django.setup()

from sales_app.models import Invoice, Sale
from django.utils import timezone

# Get today's invoices
today = timezone.now().date()
invoices = Invoice.objects.filter(date_of_sale=today).prefetch_related('items')

print(f"Invoices for {today}:")
print(f"Total invoices: {invoices.count()}")

for invoice in invoices:
    print(f"\nInvoice: {invoice.invoice_no}")
    print(f"Customer: {invoice.customer_name}")
    print(f"Total: ${invoice.total}")
    print(f"Items:")
    
    items = invoice.items.all()
    print(f"  Number of items: {items.count()}")
    
    for item in items:
        print(f"  - Item: '{item.item}'")
        print(f"    Quantity: {item.quantity}")
        print(f"    Unit Price: ${item.unit_price}")
        print(f"    Total Price: ${item.total_price}")
    
    if not items:
        print("  No items found for this invoice")
