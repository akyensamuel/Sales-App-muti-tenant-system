from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.conf import settings
from tenants.models import Tenant
from tenants.utils import ensure_tenant_database_loaded
import os


class Command(BaseCommand):
    help = 'Setup and migrate all tenant databases'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--tenant',
            help='Setup specific tenant only'
        )
    
    def handle(self, *args, **options):
        if options['tenant']:
            # Setup specific tenant
            try:
                tenant = Tenant.objects.get(subdomain=options['tenant'])
                self._setup_tenant_database(tenant)
            except Tenant.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'Tenant "{options["tenant"]}" not found')
                )
        else:
            # Setup all tenants
            self._setup_all_tenant_databases()
    
    def _setup_all_tenant_databases(self):
        """Setup databases for all tenants"""
        tenants = Tenant.objects.all()
        
        if not tenants.exists():
            self.stdout.write(self.style.WARNING('No tenants found'))
            return
        
        self.stdout.write(f'Setting up databases for {tenants.count()} tenants...\n')
        
        for tenant in tenants:
            self._setup_tenant_database(tenant)
    
    def _setup_tenant_database(self, tenant):
        """Setup database for a specific tenant"""
        self.stdout.write(f'Setting up: {tenant.name} ({tenant.subdomain})')
        
        # Load database configuration
        ensure_tenant_database_loaded(tenant)
        
        # Get database configuration
        db_config = settings.DATABASES[tenant.database_name]
        db_path = db_config['NAME']
        
        self.stdout.write(f'  Database: {db_path}')
        
        # Ensure directory exists
        db_dir = os.path.dirname(db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)
            self.stdout.write(f'  Created directory: {db_dir}')
        
        try:
            # Run migrations to create database
            self.stdout.write('  Running migrations...')
            call_command('migrate', database=tenant.database_name, verbosity=0)
            
            # Check if database was created
            if os.path.exists(db_path):
                size = os.path.getsize(db_path)
                self.stdout.write(
                    self.style.SUCCESS(f'  ✅ Database created ({size:,} bytes)')
                )
            else:
                self.stdout.write(
                    self.style.ERROR('  ❌ Database file not created')
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'  ❌ Error: {str(e)}')
            )
        
        self.stdout.write('')  # Empty line
