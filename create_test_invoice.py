#!/usr/bin/env python
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sales_management_project.settings')
sys.path.append('d:\\code\\Sales_App\\sales_management_project')
django.setup()

from sales_app.models import Invoice
from decimal import Decimal

# Create a test invoice with outstanding balance
test_invoice = Invoice.objects.create(
    customer_name="Test Customer",
    total=Decimal('1000.00'),
    amount_paid=Decimal('300.00'),
    payment_status='partial'  # This will be updated automatically by save()
)

print(f"Created test invoice: {test_invoice.invoice_no}")
print(f"Total: ${test_invoice.total}")
print(f"Paid: ${test_invoice.amount_paid}")
print(f"Balance: ${test_invoice.balance}")
print(f"Status: {test_invoice.payment_status}")

# Test the accounting dashboard calculation
from django.db.models import Sum, Count

outstanding_invoices = Invoice.objects.filter(
    payment_status__in=['unpaid', 'partial', 'overdue']
).aggregate(
    count=Count('id'),
    total=Sum('total'),
    paid=Sum('amount_paid')
)

outstanding_amount = (outstanding_invoices['total'] or 0) - (outstanding_invoices['paid'] or 0)

print(f"\nOutstanding invoices count: {outstanding_invoices['count']}")
print(f"Outstanding amount: ${outstanding_amount}")
