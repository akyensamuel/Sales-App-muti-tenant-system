from django.core.management.base import BaseCommand, CommandError
from tenants.models import Tenant
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
import re


class Command(BaseCommand):
    help = 'Create a new tenant with automatic database setup'

    def add_arguments(self, parser):
        # Required arguments
        parser.add_argument('name', type=str, help='Tenant organization name')
        parser.add_argument('subdomain', type=str, help='Tenant subdomain (alphanumeric, hyphens allowed)')
        parser.add_argument('admin_email', type=str, help='Admin email address')
        
        # Optional tenant settings
        parser.add_argument('--max-users', type=int, default=50, help='Maximum number of users (default: 50)')
        parser.add_argument('--multi-location', action='store_true', help='Enable multi-location support')
        
        # Database configuration (choose one method)
        parser.add_argument('--database-url', type=str, 
                          help='Complete database URL (e.g., postgresql://user:pass@host:port/dbname)')
        
        # Individual database parameters (alternative to --database-url)
        parser.add_argument('--database-engine', type=str, 
                          default='django.db.backends.postgresql',
                          help='Database engine (default: postgresql, use sqlite3 for local dev)')
        parser.add_argument('--database-host', type=str, help='Database host')
        parser.add_argument('--database-port', type=int, help='Database port')
        parser.add_argument('--database-user', type=str, help='Database username')
        parser.add_argument('--database-password', type=str, help='Database password')

    def handle(self, *args, **options):
        # Extract and validate inputs
        name = options['name']
        subdomain = options['subdomain'].lower()
        admin_email = options['admin_email']
        
        self.validate_inputs(name, subdomain, admin_email)
        self.validate_database_config(options)
        
        self.stdout.write(self.style.HTTP_INFO('🏗️  Creating new tenant...'))
        self.stdout.write(f"   Name: {name}")
        self.stdout.write(f"   Subdomain: {subdomain}")
        self.stdout.write(f"   Admin Email: {admin_email}")
        
        try:
            # Prepare tenant data
            tenant_data = {
                'name': name,
                'subdomain': subdomain,
                'admin_email': admin_email,
                'max_users': options['max_users'],
                'supports_multi_location': options['multi_location'],
            }
            
            # Add database configuration
            if options['database_url']:
                tenant_data['database_url'] = options['database_url']
                self.stdout.write(f"   Database: {options['database_url'][:50]}...")
            else:
                for field in ['database_engine', 'database_host', 'database_port', 
                            'database_user', 'database_password']:
                    if options[field]:
                        tenant_data[field] = options[field]
                
                if options['database_host']:
                    self.stdout.write(f"   Database: {options['database_engine']}")
                    self.stdout.write(f"   Host: {options['database_host']}:{options['database_port'] or 'default'}")
                else:
                    self.stdout.write("   Database: Auto-configured")
            
            # Create tenant (triggers automatic database setup)
            tenant = Tenant.objects.create(**tenant_data)
            
            # Show success information
            self.show_success_message(tenant)
            
        except Exception as e:
            raise CommandError(f"Failed to create tenant: {str(e)}")

    def validate_database_config(self, options):
        """Validate database configuration"""
        database_url = options.get('database_url')
        database_engine = options.get('database_engine')
        database_host = options.get('database_host')
        
        if database_url:
            # Validate URL format
            if not database_url.startswith(('postgresql://', 'mysql://', 'sqlite:///')):
                raise CommandError("Invalid database URL format. Must start with postgresql://, mysql://, or sqlite:///")
            
            if '@' in database_url and ':' in database_url:
                self.stdout.write(self.style.WARNING("⚠️  Database URL contains credentials. Ensure security."))
        
        elif database_host and 'postgresql' in database_engine:
            # Validate PostgreSQL parameters
            required = ['database_host', 'database_user', 'database_password']
            missing = [field for field in required if not options.get(field)]
            if missing:
                raise CommandError(f"Missing required PostgreSQL parameters: {', '.join(missing)}")

    def validate_inputs(self, name, subdomain, admin_email):
        """Validate all inputs"""
        # Validate name
        if len(name.strip()) < 2:
            raise CommandError("Tenant name must be at least 2 characters long")
        
        # Validate subdomain
        if not re.match(r'^[a-z0-9]([a-z0-9\-]{0,61}[a-z0-9])?$', subdomain) or len(subdomain) < 2:
            raise CommandError("Invalid subdomain. Use lowercase letters, numbers, hyphens only (2+ chars)")
        
        # Check uniqueness
        if Tenant.objects.filter(subdomain=subdomain).exists():
            raise CommandError(f"Subdomain '{subdomain}' already exists")
        
        if Tenant.objects.filter(name=name).exists():
            raise CommandError(f"Tenant name '{name}' already exists")
        
        # Validate email
        try:
            validate_email(admin_email)
        except ValidationError:
            raise CommandError("Invalid email address format")

    def show_success_message(self, tenant):
        """Display success message and next steps"""
        self.stdout.write(self.style.SUCCESS('\n🎉 TENANT CREATED SUCCESSFULLY!'))
        self.stdout.write('=' * 50)
        
        self.stdout.write(f"\n📋 Tenant Details:")
        self.stdout.write(f"   Name: {tenant.name}")
        self.stdout.write(f"   Subdomain: {tenant.subdomain}")
        self.stdout.write(f"   Admin Email: {tenant.admin_email}")
        self.stdout.write(f"   Max Users: {tenant.max_users}")
        self.stdout.write(f"   Multi-location: {'Yes' if tenant.supports_multi_location else 'No'}")
        
        self.stdout.write(f"\n🔐 Default Login:")
        self.stdout.write(f"   Username: Akyen")
        self.stdout.write(f"   Password: 08000000")
        self.stdout.write(f"   Groups: Admin, Managers, Cashiers")
        
        self.stdout.write(f"\n🌐 Access URLs:")
        self.stdout.write(f"   Main: http://{tenant.subdomain}.localhost:8000/")
        self.stdout.write(f"   Sales: http://{tenant.subdomain}.localhost:8000/sales/")
        self.stdout.write(f"   Accounting: http://{tenant.subdomain}.localhost:8000/accounting/")
        
        self.stdout.write(f"\n🛠️  Management Commands:")
        self.stdout.write(f"   Reset DB: python manage.py force_migrate_tenant {tenant.subdomain}")
        self.stdout.write(f"   Manual Setup: python manage.py manual_setup_tenant {tenant.subdomain}")
        
        self.stdout.write(f"\n⚠️  PRODUCTION CHECKLIST:")
        self.stdout.write(f"   1. Change default password immediately")
        self.stdout.write(f"   2. Update admin email if needed") 
        self.stdout.write(f"   3. Configure proper domain names")
        self.stdout.write(f"   4. Set up SSL certificates")
        self.stdout.write(f"   5. Configure database backups")
