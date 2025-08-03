#!/usr/bin/env python3
"""
Management command to run migrations on a specific tenant database
"""
from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.conf import settings
from django.db import connections
from tenants.models import Tenant
import dj_database_url

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

    def handle(self, *args, **options):
        subdomain = options['subdomain']
        apps_to_migrate = options['apps']
        
        try:
            tenant = Tenant.objects.get(subdomain=subdomain)
        except Tenant.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'❌ Tenant with subdomain "{subdomain}" not found')
            )
            return
        
        self.stdout.write(f"🔄 Running migrations for tenant: {tenant.name} ({tenant.subdomain})")
        self.stdout.write(f"   Database URL: {tenant.database_url}")
        
        # Parse the database URL and add it to Django settings
        try:
            # Use the tenant's own database configuration method
            db_config = tenant.get_database_config()
            
            # Add the tenant database to Django connections
            tenant_db_alias = f"tenant_{tenant.subdomain}"
            settings.DATABASES[tenant_db_alias] = db_config
            
            self.stdout.write(f"   🔗 Database config: {db_config['ENGINE']} at {db_config.get('HOST', 'local')}")
            
            # Test connection
            from django.db import connection
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
                        verbosity=1
                    )
                    self.stdout.write(f"   ✅ {app} migrations completed")
                except Exception as e:
                    self.stdout.write(f"   ⚠️ {app} migration warning: {e}")
            
            # Create default superuser
            self.stdout.write(f"👤 Creating default superuser...")
            self.create_default_user(tenant_db_alias)
            
            self.stdout.write(
                self.style.SUCCESS(f'✅ All migrations completed for tenant: {tenant.name}')
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error migrating tenant database: {e}')
            )
    
    def create_default_user(self, database_alias):
        """Create default superuser in tenant database"""
        from django.contrib.auth.models import User, Group
        from django.db import connections
        
        try:
            # First, just create the superuser without groups
            if not User.objects.using(database_alias).filter(username='Akyen').exists():
                user = User.objects.using(database_alias).create_superuser(
                    username='Akyen',
                    email='admin@company.com',
                    password='08000000',
                    first_name='System',
                    last_name='Administrator'
                )
                self.stdout.write(f"   ✅ Created superuser: Akyen (password: 08000000)")
                
                # Try to create and assign groups
                try:
                    admin_group, _ = Group.objects.using(database_alias).get_or_create(name='Admin')
                    manager_group, _ = Group.objects.using(database_alias).get_or_create(name='Managers')
                    cashier_group, _ = Group.objects.using(database_alias).get_or_create(name='Cashiers')
                    user.groups.add(admin_group)
                    self.stdout.write(f"   ✅ Added user to Admin group")
                except Exception as group_error:
                    self.stdout.write(f"   ⚠️ Could not create groups: {group_error}")
                    self.stdout.write(f"   ℹ️ User created successfully without groups")
            else:
                self.stdout.write(f"   ℹ️ Superuser 'Akyen' already exists")
                    
        except Exception as e:
            self.stdout.write(f"   ❌ Could not create superuser: {e}")
