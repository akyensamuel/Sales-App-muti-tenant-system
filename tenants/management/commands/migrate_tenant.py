#!/usr/bin/env python3
"""
Management command to run migrations on a specific tenant database
"""
from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.conf import settings
from django.db import connections
from tenants.models import Tenant
import os

class Command(BaseCommand):
    help = 'Run migrations on a specific tenant database'

    def add_arguments(self, parser):
        parser.add_argument(
            'subdomain',
            type=str,
            help='Subdomain of the tenant to migrate'
        )
        parser.add_argument(
            '--apps',
            type=str,
            nargs='*',
            help='Specific apps to migrate (default: all tenant apps)',
            default=['auth', 'contenttypes', 'sales_app', 'accounting_app', 'admin', 'sessions']
        )
        parser.add_argument(
            '--create-user',
            action='store_true',
            help='Create default superuser after migration'
        )

    def handle(self, *args, **options):
        subdomain = options['subdomain']
        apps_to_migrate = options['apps']
        create_user = options['create_user']
        
        try:
            tenant = Tenant.objects.get(subdomain=subdomain)
        except Tenant.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'❌ Tenant with subdomain "{subdomain}" not found')
            )
            self.stdout.write("Available tenants:")
            for t in Tenant.objects.all():
                self.stdout.write(f"   - {t.subdomain} ({t.name})")
            return
        
        self.stdout.write(f"🔄 Running migrations for tenant: {tenant.name} ({tenant.subdomain})")
        
        # Determine database configuration based on engine
        tenant_db_alias = f"tenant_db_{tenant.subdomain}"
        
        try:
            if 'sqlite3' in tenant.database_engine:
                # SQLite configuration for local development
                db_path = os.path.join('tenant_dbs', f'sales_{tenant.subdomain}.sqlite3')
                
                if not os.path.exists(db_path):
                    self.stdout.write(
                        self.style.ERROR(f'❌ SQLite database file not found: {db_path}')
                    )
                    self.stdout.write("Create the tenant first with: create_tenant command")
                    return
                
                db_config = {
                    'ENGINE': 'django.db.backends.sqlite3',
                    'NAME': db_path,
                    'OPTIONS': {},
                    'CONN_MAX_AGE': 0,
                    'AUTOCOMMIT': True,
                    'ATOMIC_REQUESTS': False,
                }
                
                self.stdout.write(f"   �️ Database: SQLite at {db_path}")
                
            else:
                # PostgreSQL configuration for production
                try:
                    db_config = tenant.get_database_config()
                    self.stdout.write(f"   🗄️ Database: PostgreSQL at {db_config.get('HOST', 'external')}")
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f'❌ Could not get database config: {e}')
                    )
                    return
            
            # Add the tenant database to Django connections
            settings.DATABASES[tenant_db_alias] = db_config
            
            # Test connection
            test_conn = connections[tenant_db_alias]
            with test_conn.cursor() as cursor:
                cursor.execute("SELECT 1")
                
            self.stdout.write(f"✅ Successfully connected to tenant database")
            
            # Run migrations for each app
            for app in apps_to_migrate:
                self.stdout.write(f"   📦 Migrating {app}...")
                try:
                    call_command(
                        'migrate', 
                        app,
                        database=tenant_db_alias,
                        verbosity=0
                    )
                    self.stdout.write(f"   ✅ {app} migrations completed")
                except Exception as e:
                    self.stdout.write(f"   ⚠️ {app} migration issue: {e}")
            
            # Create default superuser if requested
            if create_user:
                self.stdout.write(f"👤 Creating default superuser...")
                self.create_default_user(tenant_db_alias)
            
            self.stdout.write(
                self.style.SUCCESS(f'✅ All migrations completed for tenant: {tenant.name}')
            )
            self.stdout.write(f"🌐 Access URL: http://{subdomain}.localhost:8000/")
            self.stdout.write(f"🔑 Login: Akyen / 08000000")
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error migrating tenant database: {e}')
            )
            self.stdout.write("Common solutions:")
            self.stdout.write("   - Ensure the tenant was created with create_tenant command")
            self.stdout.write("   - Check database file exists (for SQLite)")
            self.stdout.write("   - Verify database credentials (for PostgreSQL)")
    
    def create_default_user(self, database_alias):
        """Create default superuser and groups in tenant database"""
        from django.contrib.auth.models import User, Group
        
        try:
            # Create default groups
            default_groups = ['Admin', 'Managers', 'Cashiers']
            created_groups = []
            
            for group_name in default_groups:
                group, created = Group.objects.using(database_alias).get_or_create(name=group_name)
                if created:
                    created_groups.append(group_name)
            
            if created_groups:
                self.stdout.write(f"   ✅ Created groups: {', '.join(created_groups)}")
            
            # Create superuser if it doesn't exist
            if not User.objects.using(database_alias).filter(username='Akyen').exists():
                user = User.objects.using(database_alias).create_superuser(
                    username='Akyen',
                    email='admin@company.com',
                    password='08000000',
                    first_name='System',
                    last_name='Administrator'
                )
                
                # Add user to all groups
                for group_name in default_groups:
                    group = Group.objects.using(database_alias).get(name=group_name)
                    user.groups.add(group)
                
                user.save(using=database_alias)
                self.stdout.write(f"   ✅ Created superuser: Akyen (password: 08000000)")
                self.stdout.write(f"   👥 Added to groups: {', '.join(default_groups)}")
            else:
                self.stdout.write(f"   ℹ️ Superuser 'Akyen' already exists")
                    
        except Exception as e:
            self.stdout.write(f"   ❌ Could not create superuser: {e}")
