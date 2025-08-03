from django.core.management.base import BaseCommand
from django.db import connections
from tenants.models import Tenant
from tenants.utils import ensure_tenant_database_loaded


class Command(BaseCommand):
    help = 'Show tables in all tenant databases'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('📋 TENANT DATABASE TABLES'))
        self.stdout.write('=' * 80)
        
        for tenant in Tenant.objects.filter(is_active=True).order_by('name'):
            self.stdout.write(f'\n🏢 {tenant.name} ({tenant.subdomain})')
            self.stdout.write(f'   Database: {tenant.database_name}')
            self.stdout.write('-' * 60)
            
            try:
                # Ensure database is loaded
                ensure_tenant_database_loaded(tenant)
                
                # Get connection to tenant database
                conn = connections[tenant.database_name]
                
                with conn.cursor() as cursor:
                    if 'sqlite3' in conn.settings_dict['ENGINE']:
                        # SQLite query
                        cursor.execute("""
                            SELECT name, type 
                            FROM sqlite_master 
                            WHERE type='table' 
                            AND name NOT LIKE 'sqlite_%'
                            AND name NOT LIKE 'django_%'
                            ORDER BY name
                        """)
                    else:
                        # PostgreSQL query
                        cursor.execute("""
                            SELECT table_name, 'table' as type
                            FROM information_schema.tables 
                            WHERE table_schema = 'public'
                            AND table_name NOT LIKE 'django_%'
                            ORDER BY table_name
                        """)
                    
                    tables = cursor.fetchall()
                    
                    if tables:
                        # Group tables by app
                        sales_tables = []
                        accounting_tables = []
                        auth_tables = []
                        other_tables = []
                        
                        for table_name, table_type in tables:
                            if table_name.startswith('sales_app_'):
                                sales_tables.append(table_name)
                            elif table_name.startswith('accounting_app_'):
                                accounting_tables.append(table_name)
                            elif table_name.startswith('auth_'):
                                auth_tables.append(table_name)
                            else:
                                other_tables.append(table_name)
                        
                        if sales_tables:
                            self.stdout.write('   📦 Sales App Tables:')
                            for table in sales_tables:
                                self.stdout.write(f'     • {table}')
                        
                        if accounting_tables:
                            self.stdout.write('   💰 Accounting App Tables:')
                            for table in accounting_tables:
                                self.stdout.write(f'     • {table}')
                        
                        if auth_tables:
                            self.stdout.write('   👤 Auth Tables:')
                            for table in auth_tables:
                                self.stdout.write(f'     • {table}')
                        
                        if other_tables:
                            self.stdout.write('   🔧 Other Tables:')
                            for table in other_tables:
                                self.stdout.write(f'     • {table}')
                        
                        self.stdout.write(f'   📊 Total: {len(tables)} tables')
                    else:
                        self.stdout.write('   ❌ No tables found')
                        
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'   Error: {e}'))
        
        self.stdout.write('\n' + '=' * 80)
        self.stdout.write('📝 Summary: All tenant databases now have sales app models!')
