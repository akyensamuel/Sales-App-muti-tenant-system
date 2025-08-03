from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group
from tenants.models import Tenant


class Command(BaseCommand):
    help = 'Set up main database with only groups and tenant configurations'

    def handle(self, *args, **options):
        self.stdout.write("🔧 Setting up main database configuration...")
        
        # Create default groups in main database
        default_groups = ['Admin', 'Managers', 'Cashiers']
        
        self.stdout.write("\n📋 Creating default groups in main database:")
        for group_name in default_groups:
            group, created = Group.objects.get_or_create(name=group_name)
            if created:
                self.stdout.write(self.style.SUCCESS(f"   ✓ Created group: {group_name}"))
            else:
                self.stdout.write(f"   ⚠️  Group already exists: {group_name}")
        
        # Display tenant database information
        self.stdout.write("\n🏢 Current tenant configurations:")
        tenants = Tenant.objects.all().order_by('name')
        
        if not tenants:
            self.stdout.write("   No tenants configured yet.")
            self.stdout.write("\n   Create a tenant using:")
            self.stdout.write("   python manage.py shell")
            self.stdout.write("   >>> from tenants.models import Tenant")
            self.stdout.write("   >>> tenant = Tenant.objects.create(")
            self.stdout.write("   ...     name='Your Company',")
            self.stdout.write("   ...     subdomain='yourcompany',")
            self.stdout.write("   ...     admin_email='admin@yourcompany.com'")
            self.stdout.write("   ... )")
        else:
            for tenant in tenants:
                self.stdout.write(f"\n   📂 {tenant.name}")
                self.stdout.write(f"      Subdomain: {tenant.subdomain}")
                self.stdout.write(f"      Database: {tenant.database_name}")
                self.stdout.write(f"      Database URL: {tenant.get_database_config()['NAME']}")
                self.stdout.write(f"      Admin Email: {tenant.admin_email}")
                self.stdout.write(f"      Active: {'✅' if tenant.is_active else '❌'}")
                self.stdout.write(f"      Access URL: http://{tenant.subdomain}.localhost:8000/")
                self.stdout.write(f"      Superuser: Akyen (password: 08000000)")
        
        self.stdout.write(self.style.SUCCESS("\n✅ Main database setup completed!"))
        self.stdout.write("\nMain database contains:")
        self.stdout.write("  - Tenant configurations and database URLs")
        self.stdout.write("  - Default groups (Admin, Managers, Cashiers)")
        self.stdout.write("  - NO user accounts (users are in tenant databases)")
        
        self.stdout.write("\nTenant databases contain:")
        self.stdout.write("  - Complete application data")
        self.stdout.write("  - User accounts and authentication")
        self.stdout.write("  - Sales and accounting records")
        self.stdout.write("  - Isolated data per organization")
