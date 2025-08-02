#!/usr/bin/env python
import os
import sys
from pathlib import Path

# Add tests directory to path and setup Django
sys.path.insert(0, str(Path(__file__).parent.parent))
from django_setup import setup_django
setup_django()

from sales_app.models import Invoice
from django.contrib.auth.models import User

# Check for invoices with null users
null_user_invoices = Invoice.objects.filter(user__isnull=True)
print(f"Found {null_user_invoices.count()} invoices with null user")

for invoice in null_user_invoices:
    print(f"Invoice {invoice.invoice_no}: user = {invoice.user}")

# Optionally, you could assign a default user or leave them as null
# The template fix should handle null users gracefully now
