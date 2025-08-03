from django.core.management.base import BaseCommand
from tenants.models import Tenant


class Command(BaseCommand):
    help = 'List all tenants and their status'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--active-only',
            action='store_true',
            help='Show only active tenants'
        )
    
    def handle(self, *args, **options):
        active_only = options['active_only']
        
        if active_only:
            tenants = Tenant.objects.filter(is_active=True)
            self.stdout.write('Active Tenants:')
        else:
            tenants = Tenant.objects.all()
            self.stdout.write('All Tenants:')
        
        if not tenants.exists():
            self.stdout.write('No tenants found.')
            return
        
        self.stdout.write('-' * 80)
        
        for tenant in tenants:
            status = '✅ Active' if tenant.is_active else '❌ Inactive'
            multi_loc = '🏢 Multi-location' if tenant.supports_multi_location else '🏪 Single location'
            
            self.stdout.write(f'Name: {tenant.name}')
            self.stdout.write(f'Subdomain: {tenant.subdomain}')
            self.stdout.write(f'Database: {tenant.database_name}')
            self.stdout.write(f'Status: {status}')
            self.stdout.write(f'Type: {multi_loc}')
            self.stdout.write(f'Max Users: {tenant.max_users}')
            self.stdout.write(f'Admin Email: {tenant.admin_email}')
            self.stdout.write(f'Created: {tenant.created_at.strftime("%Y-%m-%d %H:%M")}')
            self.stdout.write(f'URL: http://{tenant.full_domain}')
            self.stdout.write('-' * 80)
