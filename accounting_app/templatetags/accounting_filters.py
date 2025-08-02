from django import template
from django.utils import timezone
from datetime import datetime, timedelta

register = template.Library()

@register.filter
def total_outstanding(invoices):
    """Calculate total outstanding amount from a list of invoices"""
    total = 0
    for invoice in invoices:
        total += invoice.balance
    return total

@register.filter
def count_overdue(invoices):
    """Count overdue invoices"""
    count = 0
    for invoice in invoices:
        if invoice.payment_status == 'overdue':
            count += 1
    return count

@register.filter
def count_old_invoices(invoices, days):
    """Count invoices older than specified days"""
    cutoff_date = timezone.now().date() - timedelta(days=int(days))
    count = 0
    for invoice in invoices:
        if invoice.date_of_sale <= cutoff_date:
            count += 1
    return count

@register.filter
def subtract(value, arg):
    """Subtract arg from value"""
    try:
        return float(value) - float(arg)
    except (ValueError, TypeError):
        return 0
