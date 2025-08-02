from django.core.management.base import BaseCommand
from sales_app.models import Invoice

class Command(BaseCommand):
    help = 'Debug outstanding invoice amounts'

    def handle(self, *args, **options):
        # Get all unpaid/partial/overdue invoices
        outstanding_invoices = Invoice.objects.filter(
            payment_status__in=['unpaid', 'partial', 'overdue']
        )
        
        self.stdout.write(f"Total outstanding invoices: {outstanding_invoices.count()}")
        
        total_outstanding = 0
        for invoice in outstanding_invoices:
            balance = invoice.balance
            self.stdout.write(f"Invoice {invoice.invoice_no}: total=${invoice.total}, paid=${invoice.amount_paid}, balance=${balance}")
            total_outstanding += balance
            
        self.stdout.write(f"Total outstanding amount: ${total_outstanding}")
        
        # Also check aggregate calculation
        from django.db.models import Sum
        aggregate_result = outstanding_invoices.aggregate(
            total=Sum('total'),
            paid=Sum('amount_paid')
        )
        
        calculated_outstanding = (aggregate_result['total'] or 0) - (aggregate_result['paid'] or 0)
        self.stdout.write(f"Aggregate calculation result: {aggregate_result}")
        self.stdout.write(f"Calculated outstanding (aggregate): ${calculated_outstanding}")
