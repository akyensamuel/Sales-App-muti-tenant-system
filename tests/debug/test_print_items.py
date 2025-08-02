#!/usr/bin/env python
import os
import sys
from pathlib import Path

# Add tests directory to path and setup Django
sys.path.insert(0, str(Path(__file__).parent.parent))
from django_setup import setup_django
setup_django()

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
