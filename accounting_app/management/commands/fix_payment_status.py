from django.core.management.base import BaseCommand
from sales_app.models import Invoice

class Command(BaseCommand):
    help = 'Update payment status for all invoices based on amount paid'

    def handle(self, *args, **options):
        invoices = Invoice.objects.all()
        updated_count = 0
        
        for invoice in invoices:
            old_status = invoice.payment_status
            invoice.update_payment_status()
            
            if old_status != invoice.payment_status:
                invoice.save()
                updated_count += 1
                self.stdout.write(
                    f"Updated {invoice.invoice_no}: {old_status} -> {invoice.payment_status}"
                )
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully updated {updated_count} invoice(s)')
        )
