from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group
from tenants.models import Tenant
from tenants.utils import ensure_tenant_database_loaded
from tenants.middleware import set_current_tenant


class Command(BaseCommand):
    help = 'Create admin users for all tenant databases'

    def handle(self, *args, **options):
        self.stdout.write("👤 Creating admin users for tenant databases...")
        
        # Get all active tenants
        tenants = Tenant.objects.filter(is_active=True)
        
        for tenant in tenants:
            self.stdout.write(f"\n📂 Processing tenant: {tenant.name} ({tenant.subdomain})")
            
            try:
                # Set current tenant context
                set_current_tenant(tenant)
                ensure_tenant_database_loaded(tenant)
                
                # Create admin user in tenant database
                username = f"admin_{tenant.subdomain}"
                email = f"admin@{tenant.subdomain}.example.com"
                password = "admin123"  # Change this in production!
                
                # Check if user already exists
                try:
                    user = User.objects.using(tenant.database_name).get(username=username)
                    self.stdout.write(f"   User {username} already exists")
                except User.DoesNotExist:
                    # Create the user
                    user = User(
                        username=username,
                        email=email,
                        is_staff=True,
                        is_superuser=True
                    )
                    user.set_password(password)
                    user.save(using=tenant.database_name)
                    self.stdout.write(f"   ✓ Created user: {username}")
                
                # Create Admin group if it doesn't exist
                admin_group, created = Group.objects.using(tenant.database_name).get_or_create(
                    name='Admin'
                )
                if created:
                    self.stdout.write(f"   ✓ Created Admin group")
                
                # Add user to Admin group
                user.groups.add(admin_group)
                user.save(using=tenant.database_name)
                
                self.stdout.write(self.style.SUCCESS(f"   ✓ Admin user setup complete for {tenant.name}"))
                self.stdout.write(f"      Username: {username}")
                self.stdout.write(f"      Password: {password}")
                self.stdout.write(f"      Access URL: http://{tenant.subdomain}.localhost:8000/accounting/")
                
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"   ✗ Error setting up user for {tenant.name}: {str(e)}")
                )
            finally:
                # Clear tenant context
                set_current_tenant(None)
        
        self.stdout.write(self.style.SUCCESS("\n🎉 Admin user creation completed!"))
        self.stdout.write("\nYou can now test the accounting app:")
        self.stdout.write("1. http://demo.localhost:8000/accounting/ (admin_demo / admin123)")
        self.stdout.write("2. http://test.localhost:8000/accounting/ (admin_test / admin123)")
        self.stdout.write("3. http://dev.localhost:8000/accounting/ (admin_dev / admin123)")
