from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.db import connections
from django.conf import settings
from tenants.models import Tenant
from tenants.utils import ensure_tenant_database_loaded
import os


class Command(BaseCommand):
    help = 'Force apply migrations to all tenant databases with proper database loading'

    def add_arguments(self, parser):
        parser.add_argument(
            '--tenant',
            type=str,
            help='Apply to specific tenant subdomain only',
        )

    def handle(self, *args, **options):
        tenant_filter = options.get('tenant')
        
        self.stdout.write(self.style.SUCCESS('🔧 FORCE APPLYING MIGRATIONS TO TENANT DATABASES'))
        self.stdout.write('=' * 70)
        
        # Get tenants to process
        if tenant_filter:
            tenants = Tenant.objects.filter(subdomain=tenant_filter, is_active=True)
        else:
            tenants = Tenant.objects.filter(is_active=True)
        
        if not tenants.exists():
            self.stdout.write(self.style.ERROR('No tenants found'))
            return
        
        # First, load all tenant databases into Django settings
        self.stdout.write('📡 Loading tenant databases into Django settings...')
        for tenant in tenants:
            ensure_tenant_database_loaded(tenant)
            self.stdout.write(f'   ✅ Loaded: {tenant.database_name}')
        
        self.stdout.write(f'\n📊 Available databases: {list(settings.DATABASES.keys())}')
        self.stdout.write('')
        
        # Now apply migrations to each tenant database
        for tenant in tenants:
            self.stdout.write(f'🏢 Processing: {tenant.name} ({tenant.subdomain})')
            self.stdout.write(f'   Database Key: {tenant.database_name}')
            
            try:
                # Verify database configuration
                config = tenant.get_database_config()
                self.stdout.write(f'   Database Path: {config["NAME"]}')
                
                # Ensure directory exists for SQLite
                if 'sqlite3' in config.get('ENGINE', ''):
                    db_dir = os.path.dirname(config['NAME'])
                    if db_dir and not os.path.exists(db_dir):
                        os.makedirs(db_dir, exist_ok=True)
                        self.stdout.write(f'   Created directory: {db_dir}')
                
                # Apply core Django migrations first
                self.stdout.write('   📦 Applying core migrations...')
                call_command(
                    'migrate',
                    'contenttypes',
                    database=tenant.database_name,
                    verbosity=0,
                    interactive=False
                )
                call_command(
                    'migrate',
                    'auth',
                    database=tenant.database_name,
                    verbosity=0,
                    interactive=False
                )
                call_command(
                    'migrate',
                    'sessions',
                    database=tenant.database_name,
                    verbosity=0,
                    interactive=False
                )
                
                # Apply application migrations
                apps_to_migrate = ['sales_app', 'accounting_app']
                
                for app in apps_to_migrate:
                    self.stdout.write(f'   📱 Applying {app} migrations...')
                    call_command(
                        'migrate',
                        app,
                        database=tenant.database_name,
                        verbosity=1,
                        interactive=False
                    )
                
                # Verify tables were created
                self.verify_tables(tenant)
                
                self.stdout.write(f'   ✅ {tenant.name} completed successfully')
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'   ❌ Error: {e}'))
                import traceback
                traceback.print_exc()
            
            self.stdout.write('')
        
        self.stdout.write(self.style.SUCCESS('🎉 All tenant databases updated!'))

    def verify_tables(self, tenant):
        """Verify tables were created"""
        try:
            conn = connections[tenant.database_name]
            with conn.cursor() as cursor:
                if 'sqlite3' in conn.settings_dict['ENGINE']:
                    cursor.execute("""
                        SELECT name FROM sqlite_master 
                        WHERE type='table' 
                        AND (name LIKE 'sales_app_%' OR name LIKE 'accounting_app_%')
                        ORDER BY name
                    """)
                    
                    tables = [row[0] for row in cursor.fetchall()]
                    
                    if tables:
                        self.stdout.write(f'   📋 Created tables: {", ".join(tables)}')
                    else:
                        self.stdout.write(f'   ⚠️  No application tables found')
                        
        except Exception as e:
            self.stdout.write(f'   ⚠️  Verification failed: {e}')
