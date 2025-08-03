#!/usr/bin/env python3
"""
Reset tenant database migrations and recreate tables
"""
from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.conf import settings
from django.db import connections
from tenants.models import Tenant
import psycopg2

class Command(BaseCommand):
    help = 'Reset and recreate tenant database with fresh migrations'

    def add_arguments(self, parser):
        parser.add_argument(
            'subdomain',
            type=str,
            help='Subdomain of the tenant to reset'
        )

    def handle(self, *args, **options):
        subdomain = options['subdomain']
        
        try:
            tenant = Tenant.objects.get(subdomain=subdomain)
        except Tenant.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'❌ Tenant with subdomain "{subdomain}" not found')
            )
            return
        
        self.stdout.write(f"🔄 Resetting tenant database: {tenant.name} ({tenant.subdomain})")
        self.stdout.write(f"   Database URL: {tenant.database_url}")
        
        # Connect directly to PostgreSQL and drop/create tables
        try:
            # Use tenant's database configuration
            db_config = tenant.get_database_config()
            
            self.stdout.write("🗑️ Dropping existing tables...")
            
            # Handle potential empty PORT value
            port = db_config.get('PORT', 5432)
            if not port or port == '':
                port = 5432
            
            conn = psycopg2.connect(
                host=db_config['HOST'],
                port=int(port),
                database=db_config['NAME'],
                user=db_config['USER'],
                password=db_config['PASSWORD']
            )
            conn.autocommit = True
            cursor = conn.cursor()
            
            # Get all tables
            cursor.execute("""
                SELECT table_name FROM information_schema.tables 
                WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
            """)
            tables = [row[0] for row in cursor.fetchall()]
            
            self.stdout.write(f"   Found {len(tables)} tables to drop")
            
            # Drop all tables
            for table in tables:
                cursor.execute(f'DROP TABLE IF EXISTS "{table}" CASCADE')
                
            cursor.close()
            conn.close()
            
            self.stdout.write("✅ Tables dropped successfully")
            
            # Now run fresh migrations
            self.stdout.write("🔧 Running fresh migrations...")
            
            # Setup Django database connection
            db_config = tenant.get_database_config()
            tenant_db_alias = f"tenant_{tenant.subdomain}"
            settings.DATABASES[tenant_db_alias] = db_config
            
            # Run migrations
            apps_to_migrate = ['contenttypes', 'auth', 'admin', 'sessions', 'sales_app', 'accounting_app']
            
            for app in apps_to_migrate:
                self.stdout.write(f"   📦 Migrating {app}...")
                call_command('migrate', app, database=tenant_db_alias, verbosity=0)
                self.stdout.write(f"   ✅ {app} completed")
            
            # Create superuser
            self.stdout.write(f"👤 Creating default superuser...")
            self.create_superuser(tenant_db_alias)
            
            self.stdout.write(
                self.style.SUCCESS(f'✅ Tenant database reset completed: {tenant.name}')
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error resetting tenant database: {e}')
            )
    
    def create_superuser(self, database_alias):
        """Create default superuser in tenant database"""
        try:
            from django.contrib.auth.models import User, Group
            
            # Create groups
            manager_group, _ = Group.objects.using(database_alias).get_or_create(name='Managers')
            sales_group, _ = Group.objects.using(database_alias).get_or_create(name='Sales Team')
            
            # Create superuser
            if not User.objects.using(database_alias).filter(username='Akyen').exists():
                user = User.objects.using(database_alias).create_superuser(
                    username='Akyen',
                    email='admin@company.com',
                    password='08000000',
                    first_name='System',
                    last_name='Administrator'
                )
                user.groups.add(manager_group)
                self.stdout.write(f"   ✅ Created superuser: Akyen (password: 08000000)")
            else:
                self.stdout.write(f"   ℹ️ Superuser 'Akyen' already exists")
                
        except Exception as e:
            self.stdout.write(f"   ⚠️ Error creating superuser: {e}")
