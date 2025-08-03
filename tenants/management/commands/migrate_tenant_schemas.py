from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.db import connection
from django.conf import settings
from tenants.models import Tenant
from tenants.utils import ensure_tenant_database_loaded
import os


class Command(BaseCommand):
    help = 'Apply all sales models (migrations) to all tenant databases'

    def add_arguments(self, parser):
        parser.add_argument(
            '--tenant',
            type=str,
            help='Apply to specific tenant subdomain only',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be done without actually doing it',
        )

    def handle(self, *args, **options):
        tenant_filter = options.get('tenant')
        dry_run = options.get('dry_run')
        
        self.stdout.write(self.style.SUCCESS('🗄️  APPLYING SALES MODELS TO TENANT DATABASES'))
        self.stdout.write('=' * 70)
        
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - No changes will be made'))
            self.stdout.write('')
        
        # Get tenants to process
        if tenant_filter:
            tenants = Tenant.objects.filter(subdomain=tenant_filter, is_active=True)
            if not tenants.exists():
                self.stdout.write(self.style.ERROR(f'Tenant "{tenant_filter}" not found or inactive'))
                return
        else:
            tenants = Tenant.objects.filter(is_active=True)
        
        if not tenants.exists():
            self.stdout.write(self.style.ERROR('No active tenants found'))
            return
        
        self.stdout.write(f'Found {tenants.count()} tenant(s) to process:')
        for tenant in tenants:
            self.stdout.write(f'  • {tenant.name} ({tenant.subdomain})')
        self.stdout.write('')
        
        # Apps to migrate to tenant databases
        tenant_apps = ['sales_app', 'accounting_app', 'core']
        
        for tenant in tenants:
            self.stdout.write(f'📊 Processing tenant: {tenant.name}')
            self.stdout.write(f'   Subdomain: {tenant.subdomain}')
            self.stdout.write(f'   Database: {tenant.database_name}')
            
            if dry_run:
                self.stdout.write(f'   Would migrate apps: {", ".join(tenant_apps)}')
                self.stdout.write('')
                continue
            
            try:
                # Ensure tenant database is loaded
                ensure_tenant_database_loaded(tenant)
                
                # Check if database file exists (for SQLite)
                config = tenant.get_database_config()
                if 'sqlite3' in config.get('ENGINE', ''):
                    db_path = config['NAME']
                    if not os.path.exists(db_path):
                        self.stdout.write(f'   Creating database file: {db_path}')
                        os.makedirs(os.path.dirname(db_path), exist_ok=True)
                
                # Apply migrations for each app
                for app in tenant_apps:
                    self.stdout.write(f'   ⚙️  Migrating {app}...')
                    
                    try:
                        call_command(
                            'migrate',
                            app,
                            database=tenant.database_name,
                            verbosity=0,
                            interactive=False
                        )
                        self.stdout.write(f'   ✅ {app} migrated successfully')
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f'   ❌ Error migrating {app}: {e}'))
                
                # Verify tables were created
                self.verify_tenant_tables(tenant)
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'   ❌ Error processing tenant: {e}'))
            
            self.stdout.write('')
        
        self.stdout.write(self.style.SUCCESS('✅ Migration process completed!'))
        self.stdout.write('')
        self.show_tenant_summary()

    def verify_tenant_tables(self, tenant):
        """Verify that tenant database has the expected tables"""
        try:
            from django.db import connections
            
            conn = connections[tenant.database_name]
            
            with conn.cursor() as cursor:
                # Check for key sales app tables
                expected_tables = [
                    'sales_app_product',
                    'sales_app_invoice', 
                    'sales_app_sale',
                    'accounting_app_expense',
                    'accounting_app_expensecategory'
                ]
                
                if 'sqlite3' in conn.settings_dict['ENGINE']:
                    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'sales_app_%' OR name LIKE 'accounting_app_%'")
                else:
                    cursor.execute("""
                        SELECT table_name FROM information_schema.tables 
                        WHERE table_schema = 'public' 
                        AND (table_name LIKE 'sales_app_%' OR table_name LIKE 'accounting_app_%')
                    """)
                
                existing_tables = [row[0] for row in cursor.fetchall()]
                
                found_tables = [table for table in expected_tables if table in existing_tables]
                
                if found_tables:
                    self.stdout.write(f'   📋 Found {len(found_tables)} application tables')
                else:
                    self.stdout.write(self.style.WARNING(f'   ⚠️  No application tables found'))
                    
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'   ⚠️  Could not verify tables: {e}'))

    def show_tenant_summary(self):
        """Show summary of all tenant databases"""
        self.stdout.write('📊 TENANT DATABASE SUMMARY:')
        self.stdout.write('-' * 40)
        
        for tenant in Tenant.objects.filter(is_active=True):
            config = tenant.get_database_config()
            
            if 'sqlite3' in config.get('ENGINE', ''):
                db_path = config['NAME']
                if os.path.exists(db_path):
                    size = os.path.getsize(db_path)
                    self.stdout.write(f'{tenant.name:20} | {size:>8,} bytes | {tenant.subdomain}.localhost:8000')
                else:
                    self.stdout.write(f'{tenant.name:20} | {"Missing":>8} | {tenant.subdomain}.localhost:8000')
            else:
                self.stdout.write(f'{tenant.name:20} | {"External":>8} | {tenant.subdomain}.localhost:8000')
