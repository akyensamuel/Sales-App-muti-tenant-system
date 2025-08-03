from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.conf import settings
from tenants.models import Tenant
from tenants.utils import ensure_tenant_database_loaded


class Command(BaseCommand):
    help = 'Migrate auth tables to all tenant databases'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force migration even if tables already exist',
        )

    def handle(self, *args, **options):
        self.stdout.write("Migrating auth tables to tenant databases...")
        
        # Get all active tenants
        tenants = Tenant.objects.filter(is_active=True)
        
        for tenant in tenants:
            self.stdout.write(f"\n📂 Processing tenant: {tenant.name} ({tenant.subdomain})")
            
            try:
                # Ensure tenant database is loaded
                ensure_tenant_database_loaded(tenant)
                
                # Run contenttypes migrations first (required for auth)
                self.stdout.write(f"   Running contenttypes migrations on {tenant.database_name}...")
                call_command('migrate', 'contenttypes', database=tenant.database_name, verbosity=0)
                
                # Run auth migrations on tenant database
                self.stdout.write(f"   Running auth migrations on {tenant.database_name}...")
                call_command('migrate', 'auth', database=tenant.database_name, verbosity=0)
                
                self.stdout.write(self.style.SUCCESS(f"   ✓ Auth tables created for {tenant.name}"))
                
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"   ✗ Error migrating {tenant.name}: {str(e)}")
                )
        
        self.stdout.write(self.style.SUCCESS("\n🎉 Auth migration to tenant databases completed!"))
        self.stdout.write("\nNext steps:")
        self.stdout.write("1. Create admin users in each tenant database")
        self.stdout.write("2. Test access to /accounting/ through tenant subdomains")
