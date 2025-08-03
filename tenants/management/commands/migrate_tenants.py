from django.core.management.base import BaseCommand, CommandError
from django.core.management import call_command
from tenants.models import Tenant


class Command(BaseCommand):
    help = 'Migrate all tenant databases'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--tenant',
            type=str,
            help='Migrate specific tenant only (by subdomain)'
        )
        parser.add_argument(
            '--app',
            type=str,
            help='Migrate specific app only'
        )
    
    def handle(self, *args, **options):
        tenant_filter = options.get('tenant')
        app_filter = options.get('app')
        
        if tenant_filter:
            # Migrate specific tenant
            try:
                tenant = Tenant.objects.get(subdomain=tenant_filter)
                self._migrate_tenant(tenant, app_filter)
            except Tenant.DoesNotExist:
                raise CommandError(f'Tenant with subdomain "{tenant_filter}" not found')
        else:
            # Migrate all tenants
            tenants = Tenant.objects.filter(is_active=True)
            
            if not tenants.exists():
                self.stdout.write('No active tenants found.')
                return
            
            self.stdout.write(f'Migrating {tenants.count()} tenant(s)...')
            
            for tenant in tenants:
                self._migrate_tenant(tenant, app_filter)
        
        self.stdout.write(self.style.SUCCESS('All tenant migrations completed successfully!'))
    
    def _migrate_tenant(self, tenant, app_filter=None):
        """Migrate a specific tenant database"""
        self.stdout.write(f'Migrating tenant: {tenant.name} ({tenant.subdomain})...')
        
        try:
            if app_filter:
                call_command('migrate', app_filter, database=tenant.database_name, verbosity=1)
            else:
                call_command('migrate', database=tenant.database_name, verbosity=1)
            
            self.stdout.write(
                self.style.SUCCESS(f'✅ Successfully migrated {tenant.subdomain}')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Failed to migrate {tenant.subdomain}: {str(e)}')
            )
