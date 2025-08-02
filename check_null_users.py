#!/usr/bin/env python
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sales_management_project.settings')
sys.path.append('d:\\code\\Sales_App\\sales_management_project')
django.setup()

from sales_app.models import Invoice
from django.contrib.auth.models import User

# Check for invoices with null users
null_user_invoices = Invoice.objects.filter(user__isnull=True)
print(f"Found {null_user_invoices.count()} invoices with null user")

for invoice in null_user_invoices:
    print(f"Invoice {invoice.invoice_no}: user = {invoice.user}")

# Optionally, you could assign a default user or leave them as null
# The template fix should handle null users gracefully now
