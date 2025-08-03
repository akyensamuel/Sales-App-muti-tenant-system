from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.conf import settings
from tenants.models import Tenant
from tenants.utils import ensure_tenant_database_loaded
import os


class Command(BaseCommand):
    help = 'Reset and recreate all tenant databases with complete schema'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force reset even if databases exist',
        )

    def handle(self, *args, **options):
        self.stdout.write("🔄 Resetting and recreating tenant databases...")
        
        # Get all active tenants
        tenants = Tenant.objects.filter(is_active=True)
        
        for tenant in tenants:
            self.stdout.write(f"\n📂 Processing tenant: {tenant.name} ({tenant.subdomain})")
            
            try:
                # Remove existing tenant database file if it exists
                db_path = f"tenant_dbs/{tenant.database_name}.sqlite3"
                if os.path.exists(db_path):
                    self.stdout.write(f"   Removing existing database: {db_path}")
                    os.remove(db_path)
                
                # Ensure tenant database is loaded
                ensure_tenant_database_loaded(tenant)
                
                # Run all migrations on tenant database
                self.stdout.write(f"   Running all migrations on {tenant.database_name}...")
                
                # Run migrations for all apps that should be in tenant databases
                apps_to_migrate = ['contenttypes', 'auth', 'sales_app', 'accounting_app']
                
                for app in apps_to_migrate:
                    self.stdout.write(f"     Migrating {app}...")
                    call_command('migrate', app, database=tenant.database_name, verbosity=0)
                
                self.stdout.write(self.style.SUCCESS(f"   ✓ Complete database created for {tenant.name}"))
                
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"   ✗ Error creating database for {tenant.name}: {str(e)}")
                )
        
        self.stdout.write(self.style.SUCCESS("\n🎉 Tenant database reset completed!"))
        self.stdout.write("\nNext steps:")
        self.stdout.write("1. Create admin users in each tenant database")
        self.stdout.write("2. Test access to /accounting/ through tenant subdomains")
        self.stdout.write("   - http://demo.localhost:8000/accounting/")
        self.stdout.write("   - http://test.localhost:8000/accounting/")
        self.stdout.write("   - http://dev.localhost:8000/accounting/")
