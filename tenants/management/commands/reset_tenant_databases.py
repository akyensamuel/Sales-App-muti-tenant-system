from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.db import connections
from django.conf import settings
from tenants.models import Tenant
from tenants.utils import ensure_tenant_database_loaded
import os


class Command(BaseCommand):
    help = 'Reset and recreate all tables in tenant databases'

    def add_arguments(self, parser):
        parser.add_argument(
            '--tenant',
            type=str,
            help='Reset specific tenant subdomain only',
        )
        parser.add_argument(
            '--confirm',
            action='store_true',
            help='Confirm that you want to reset tenant databases',
        )

    def handle(self, *args, **options):
        tenant_filter = options.get('tenant')
        confirm = options.get('confirm')
        
        if not confirm:
            self.stdout.write(self.style.ERROR('⚠️  WARNING: This will reset tenant databases!'))
            self.stdout.write('Add --confirm to proceed')
            return
        
        self.stdout.write(self.style.SUCCESS('🔄 RESETTING TENANT DATABASES'))
        self.stdout.write('=' * 70)
        
        # Get tenants to process
        if tenant_filter:
            tenants = Tenant.objects.filter(subdomain=tenant_filter, is_active=True)
        else:
            tenants = Tenant.objects.filter(is_active=True)
        
        if not tenants.exists():
            self.stdout.write(self.style.ERROR('No tenants found'))
            return
        
        # Load all tenant databases
        for tenant in tenants:
            ensure_tenant_database_loaded(tenant)
        
        for tenant in tenants:
            self.stdout.write(f'🏢 Resetting: {tenant.name} ({tenant.subdomain})')
            
            try:
                config = tenant.get_database_config()
                db_path = config['NAME']
                
                # Delete and recreate SQLite database
                if 'sqlite3' in config.get('ENGINE', ''):
                    if os.path.exists(db_path):
                        os.remove(db_path)
                        self.stdout.write(f'   🗑️  Deleted old database: {db_path}')
                    
                    # Ensure directory exists
                    db_dir = os.path.dirname(db_path)
                    if db_dir and not os.path.exists(db_dir):
                        os.makedirs(db_dir, exist_ok=True)
                
                # Run fresh migrations
                self.stdout.write('   📦 Creating fresh database with all tables...')
                
                # Apply all migrations
                call_command(
                    'migrate',
                    database=tenant.database_name,
                    verbosity=1,
                    interactive=False
                )
                
                # Verify tables
                self.verify_tables(tenant)
                
                self.stdout.write(f'   ✅ {tenant.name} reset successfully')
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'   ❌ Error: {e}'))
                import traceback
                traceback.print_exc()
            
            self.stdout.write('')
        
        self.stdout.write(self.style.SUCCESS('🎉 All tenant databases reset!'))

    def verify_tables(self, tenant):
        """Verify tables were created"""
        try:
            conn = connections[tenant.database_name]
            with conn.cursor() as cursor:
                if 'sqlite3' in conn.settings_dict['ENGINE']:
                    cursor.execute("""
                        SELECT name FROM sqlite_master 
                        WHERE type='table' 
                        AND name NOT LIKE 'django_%'
                        AND name NOT LIKE 'sqlite_%'
                        ORDER BY name
                    """)
                    
                    tables = [row[0] for row in cursor.fetchall()]
                    
                    if tables:
                        # Group by app
                        sales_tables = [t for t in tables if t.startswith('sales_app_')]
                        accounting_tables = [t for t in tables if t.startswith('accounting_app_')]
                        auth_tables = [t for t in tables if t.startswith('auth_')]
                        
                        self.stdout.write(f'   📊 Created {len(tables)} tables:')
                        if sales_tables:
                            self.stdout.write(f'      📦 Sales: {len(sales_tables)} tables')
                        if accounting_tables:
                            self.stdout.write(f'      💰 Accounting: {len(accounting_tables)} tables')
                        if auth_tables:
                            self.stdout.write(f'      👤 Auth: {len(auth_tables)} tables')
                    else:
                        self.stdout.write(f'   ⚠️  No application tables found')
                        
        except Exception as e:
            self.stdout.write(f'   ⚠️  Verification failed: {e}')
