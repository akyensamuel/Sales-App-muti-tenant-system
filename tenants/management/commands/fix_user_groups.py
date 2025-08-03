from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group
from django.db import connections
from tenants.models import Tenant
import os

class Command(BaseCommand):
    help = 'Fix user group assignments for a tenant'

    def add_arguments(self, parser):
        parser.add_argument('subdomain', type=str, help='Tenant subdomain')

    def handle(self, *args, **options):
        subdomain = options['subdomain']
        
        try:
            # Get tenant
            tenant = Tenant.objects.get(subdomain=subdomain)
            self.stdout.write(f"🔧 Fixing user groups for tenant: {tenant.name}")
            
            # Get database config
            database_alias = f'tenant_db_{subdomain}'
            
            # Configure tenant database connection
            if 'sqlite3' in tenant.database_engine:
                database_path = os.path.join('tenant_dbs', f'sales_{subdomain}.sqlite3')
                connections.databases[database_alias] = {
                    'ENGINE': 'django.db.backends.sqlite3',
                    'NAME': database_path
                }
            else:
                # Handle PostgreSQL if needed
                self.stdout.write(self.style.ERROR("PostgreSQL configuration not implemented in this fix command"))
                return
            
            # Ensure groups exist in tenant database
            required_groups = ['Admin', 'Managers', 'Cashiers']
            for group_name in required_groups:
                group, created = Group.objects.using(database_alias).get_or_create(name=group_name)
                if created:
                    self.stdout.write(f"   ✅ Created group: {group_name}")
                else:
                    self.stdout.write(f"   ✅ Group exists: {group_name}")
            
            # Get or create the default user
            try:
                user = User.objects.using(database_alias).get(username='Akyen')
                self.stdout.write(f"   👤 Found user: {user.username}")
            except User.DoesNotExist:
                # Create the user if it doesn't exist
                user = User.objects.using(database_alias).create_superuser(
                    username='Akyen',
                    email='lordsades1@gmail.com',
                    password='08000000'
                )
                self.stdout.write(f"   👤 Created user: {user.username}")
            
            # Clear existing groups and add all required groups
            user.groups.using(database_alias).clear()
            
            for group_name in required_groups:
                group = Group.objects.using(database_alias).get(name=group_name)
                user.groups.add(group)
                self.stdout.write(f"   ✅ Added user to group: {group_name}")
            
            # Save user
            user.save(using=database_alias)
            
            # Verify groups
            user_groups = [g.name for g in user.groups.using(database_alias).all()]
            self.stdout.write(f"\n🎉 SUCCESS! User '{user.username}' is now in groups: {user_groups}")
            
            self.stdout.write(f"\n📱 Access your tenant:")
            self.stdout.write(f"   URL: http://{subdomain}.localhost:8000/")
            self.stdout.write(f"   Username: Akyen")
            self.stdout.write(f"   Password: 08000000")
            
        except Tenant.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"Tenant with subdomain '{subdomain}' not found"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error: {str(e)}"))
