#!/usr/bin/env python
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sales_management_project.settings')
sys.path.append('d:\\code\\Sales_App\\sales_management_project')
django.setup()

from sales_app.models import Invoice
from django.db.models import Sum, Count

print("=== Invoice Data Analysis ===")

# Get all invoices
invoices = Invoice.objects.all()
print(f"Total invoices in database: {invoices.count()}")

# Show details of each invoice
for invoice in invoices:
    print(f"Invoice {invoice.invoice_no}:")
    print(f"  - Total: ${invoice.total}")
    print(f"  - Amount Paid: ${invoice.amount_paid}")
    print(f"  - Payment Status: {invoice.payment_status}")
    print(f"  - Balance: ${invoice.balance}")
    print()

# Get outstanding invoices
outstanding_invoices = Invoice.objects.filter(
    payment_status__in=['unpaid', 'partial', 'overdue']
)

print(f"Outstanding invoices count: {outstanding_invoices.count()}")

# Aggregate calculation
aggregate_result = outstanding_invoices.aggregate(
    count=Count('id'),
    total=Sum('total'),
    paid=Sum('amount_paid')
)

print(f"Aggregate result: {aggregate_result}")

outstanding_amount = (aggregate_result['total'] or 0) - (aggregate_result['paid'] or 0)
print(f"Calculated outstanding amount: ${outstanding_amount}")

# Manual calculation
manual_total = 0
for invoice in outstanding_invoices:
    manual_total += invoice.balance
    
print(f"Manual calculation total: ${manual_total}")
