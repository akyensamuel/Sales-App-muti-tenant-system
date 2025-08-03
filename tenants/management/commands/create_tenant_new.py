from django.core.management.base import BaseCommand, CommandError
from tenants.models import Tenant
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
import re


class Command(BaseCommand):
    help = 'Create a new tenant with automatic database setup'

    def add_arguments(self, parser):
        parser.add_argument('name', type=str, help='Tenant organization name')
        parser.add_argument('subdomain', type=str, help='Tenant subdomain')
        parser.add_argument('admin_email', type=str, help='Admin email address')
        parser.add_argument(
            '--max-users',
            type=int,
            default=50,
            help='Maximum number of users (default: 50)'
        )
        parser.add_argument(
            '--multi-location',
            action='store_true',
            help='Enable multi-location support'
        )

    def handle(self, *args, **options):
        name = options['name']
        subdomain = options['subdomain'].lower()
        admin_email = options['admin_email']
        max_users = options['max_users']
        multi_location = options['multi_location']
        
        # Validate inputs
        self.validate_inputs(name, subdomain, admin_email)
        
        self.stdout.write(f"🏢 Creating new tenant: {name}")
        self.stdout.write(f"   Subdomain: {subdomain}")
        self.stdout.write(f"   Admin Email: {admin_email}")
        self.stdout.write(f"   Max Users: {max_users}")
        self.stdout.write(f"   Multi-location: {'Yes' if multi_location else 'No'}")
        
        try:
            # Create the tenant (this will auto-trigger database setup)
            tenant = Tenant.objects.create(
                name=name,
                subdomain=subdomain,
                admin_email=admin_email,
                max_users=max_users,
                supports_multi_location=multi_location
            )
            
            self.stdout.write(self.style.SUCCESS(f"\n🎉 Tenant '{name}' created successfully!"))
            self.stdout.write("\n📋 Tenant Details:")
            self.stdout.write(f"   Name: {tenant.name}")
            self.stdout.write(f"   Subdomain: {tenant.subdomain}")
            self.stdout.write(f"   Database: {tenant.database_name}")
            self.stdout.write(f"   Admin Email: {tenant.admin_email}")
            
            self.stdout.write("\n🔐 Default Superuser Created:")
            self.stdout.write("   Username: Akyen")
            self.stdout.write("   Password: 08000000")
            self.stdout.write("   Email: lordsades1@gmail.com")
            
            self.stdout.write("\n👥 Default Groups Created:")
            self.stdout.write("   - Admin")
            self.stdout.write("   - Managers") 
            self.stdout.write("   - Cashiers")
            
            self.stdout.write("\n🌐 Access URLs:")
            self.stdout.write(f"   Main App: http://{tenant.subdomain}.localhost:8000/")
            self.stdout.write(f"   Accounting: http://{tenant.subdomain}.localhost:8000/accounting/")
            self.stdout.write(f"   Sales: http://{tenant.subdomain}.localhost:8000/sales/")
            
            self.stdout.write("\n⚠️  PRODUCTION NOTES:")
            self.stdout.write("   1. Change default password immediately")
            self.stdout.write("   2. Update admin email if needed")
            self.stdout.write("   3. Configure proper domain names (not .localhost)")
            self.stdout.write("   4. Set up SSL certificates")
            self.stdout.write("   5. Configure backup procedures")
            
        except Exception as e:
            raise CommandError(f"Failed to create tenant: {str(e)}")

    def validate_inputs(self, name, subdomain, admin_email):
        """Validate tenant creation inputs"""
        
        # Validate tenant name
        if len(name.strip()) < 2:
            raise CommandError("Tenant name must be at least 2 characters long")
        
        # Validate subdomain
        subdomain_pattern = r'^[a-z0-9]([a-z0-9\-]{0,61}[a-z0-9])?$'
        if not re.match(subdomain_pattern, subdomain):
            raise CommandError("Invalid subdomain format. Use lowercase letters, numbers, and hyphens only")
        
        if len(subdomain) < 2:
            raise CommandError("Subdomain must be at least 2 characters long")
        
        # Check if subdomain already exists
        if Tenant.objects.filter(subdomain=subdomain).exists():
            raise CommandError(f"Subdomain '{subdomain}' already exists")
        
        # Validate email
        try:
            validate_email(admin_email)
        except ValidationError:
            raise CommandError("Invalid email address format")
        
        # Check if tenant name already exists
        if Tenant.objects.filter(name=name).exists():
            raise CommandError(f"Tenant name '{name}' already exists")
