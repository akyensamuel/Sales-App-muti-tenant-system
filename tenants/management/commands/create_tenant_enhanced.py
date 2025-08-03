#!/usr/bin/env python3
"""
Enhanced management command to create tenants with streamlined process
"""
from django.core.management.base import BaseCommand, CommandError
from tenants.models import Tenant
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
import re
import os
from urllib.parse import urlparse


class Command(BaseCommand):
    help = 'Create a new tenant with automatic database setup and migrations'

    def add_arguments(self, parser):
        # Required arguments
        parser.add_argument('name', type=str, help='Tenant organization name')
        parser.add_argument('subdomain', type=str, help='Tenant subdomain (alphanumeric, hyphens allowed)')
        parser.add_argument('admin_email', type=str, help='Admin email address')
        
        # Optional tenant settings
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
        
        # Database configuration (choose one method)
        parser.add_argument(
            '--database-url',
            type=str,
            help='Complete database URL (recommended for production)'
        )
        
        # Individual database parameters (alternative to --database-url)
        parser.add_argument(
            '--database-engine',
            type=str,
            choices=[
                'django.db.backends.postgresql',
                'django.db.backends.mysql',
                'django.db.backends.sqlite3'
            ],
            default='django.db.backends.sqlite3',
            help='Database engine (default: sqlite3 for development)'
        )
        parser.add_argument(
            '--database-host',
            type=str,
            help='Database host (required for PostgreSQL/MySQL)'
        )
        parser.add_argument(
            '--database-port',
            type=int,
            help='Database port (5432 for PostgreSQL, 3306 for MySQL)'
        )
        parser.add_argument(
            '--database-user',
            type=str,
            help='Database username (required for PostgreSQL/MySQL)'
        )
        parser.add_argument(
            '--database-password',
            type=str,
            help='Database password (required for PostgreSQL/MySQL)'
        )
        parser.add_argument(
            '--database-name',
            type=str,
            help='Database name (auto-generated if not provided)'
        )
        
        # Migration and setup options
        parser.add_argument(
            '--skip-migrations',
            action='store_true',
            help='Skip running migrations (useful for production where you run migrations manually)'
        )
        parser.add_argument(
            '--force-setup',
            action='store_true',
            help='Force database setup even if tables already exist'
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.HTTP_INFO('🏗️  Creating new tenant...'))
        
        try:
            # Validate input
            self.validate_input(options)
            
            # Check if tenant already exists
            if Tenant.objects.filter(subdomain=options['subdomain']).exists():
                raise CommandError(f"❌ Tenant with subdomain '{options['subdomain']}' already exists")
            
            # Create tenant
            tenant = self.create_tenant(options)
            
            # Setup database if not skipped
            if not options['skip_migrations']:
                self.setup_tenant_database(tenant, options)
            else:
                self.stdout.write(
                    self.style.WARNING('⚠️  Skipping migrations. Run migrations manually in production.')
                )
            
            # Show success message
            self.show_success_message(tenant, options)
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Error creating tenant: {e}'))
            raise CommandError(str(e))

    def validate_input(self, options):
        """Validate all input parameters"""
        # Validate email
        try:
            validate_email(options['admin_email'])
        except ValidationError:
            raise CommandError(f"❌ Invalid email address: {options['admin_email']}")
        
        # Validate subdomain
        if not re.match(r'^[a-z0-9][a-z0-9-]*[a-z0-9]$', options['subdomain']) or len(options['subdomain']) < 2:
            raise CommandError(
                "❌ Subdomain must be 2+ characters, start/end with alphanumeric, and contain only lowercase letters, numbers, and hyphens"
            )
        
        # Validate database configuration
        if options['database_url']:
            try:
                parsed = urlparse(options['database_url'])
                if not parsed.scheme or not parsed.hostname:
                    raise ValueError("Invalid URL format")
            except Exception:
                raise CommandError("❌ Invalid database URL format")
        else:
            # If using individual parameters, validate required ones for non-SQLite
            if options['database_engine'] != 'django.db.backends.sqlite3':
                required_params = ['database_host', 'database_user', 'database_password']
                missing = [param for param in required_params if not options[param]]
                if missing:
                    raise CommandError(
                        f"❌ Missing required database parameters for {options['database_engine']}: {', '.join(missing)}"
                    )

    def create_tenant(self, options):
        """Create the tenant record"""
        self.stdout.write(f"📝 Creating tenant record...")
        
        tenant_data = {
            'name': options['name'],
            'subdomain': options['subdomain'],
            'admin_email': options['admin_email'],
            'max_users': options['max_users'],
            'supports_multi_location': options['multi_location'],
        }
        
        # Add database configuration
        if options['database_url']:
            tenant_data['database_url'] = options['database_url']
        else:
            tenant_data.update({
                'database_engine': options['database_engine'],
                'database_host': options['database_host'],
                'database_port': options['database_port'],
                'database_user': options['database_user'],
                'database_password': options['database_password'],
                'database_name': options['database_name'] or f"tenant_{options['subdomain']}",
            })
        
        # Create tenant (this will NOT trigger automatic setup due to skip_migrations)
        tenant = Tenant(**tenant_data)
        tenant.save()
        
        self.stdout.write(self.style.SUCCESS(f"✅ Tenant '{tenant.name}' created successfully"))
        return tenant

    def setup_tenant_database(self, tenant, options):
        """Setup tenant database with migrations and default data"""
        self.stdout.write(f"🔧 Setting up tenant database...")
        
        # Check if it's a remote database or local
        is_remote = self.is_remote_database(tenant)
        
        if is_remote:
            self.stdout.write(f"📡 Remote database detected: {tenant.database_url or 'Individual parameters'}")
            
            # Try to run migrations
            try:
                from django.core.management import call_command
                
                # Use our enhanced migrate_tenant command
                call_command('migrate_tenant', tenant.subdomain)
                self.stdout.write(self.style.SUCCESS(f"✅ Database migrations completed"))
                
            except Exception as e:
                self.stdout.write(self.style.WARNING(f"⚠️  Could not run migrations automatically: {e}"))
                self.stdout.write(f"📋 To complete setup manually, run:")
                self.stdout.write(f"   python manage.py migrate_tenant {tenant.subdomain}")
        else:
            # Local SQLite - run full setup
            self.stdout.write(f"💾 Local SQLite database detected")
            try:
                tenant.setup_tenant_database()
                self.stdout.write(self.style.SUCCESS(f"✅ Local database setup completed"))
            except Exception as e:
                self.stdout.write(self.style.WARNING(f"⚠️  Local setup warning: {e}"))

    def is_remote_database(self, tenant):
        """Check if this is a remote database connection"""
        if tenant.database_url:
            return 'postgresql://' in tenant.database_url or 'mysql://' in tenant.database_url
        return tenant.database_engine != 'django.db.backends.sqlite3'

    def show_success_message(self, tenant, options):
        """Display success message with next steps"""
        self.stdout.write(self.style.HTTP_SUCCESS('🎉 TENANT CREATION SUCCESSFUL!'))
        self.stdout.write('=' * 60)
        self.stdout.write(f"📋 Tenant Details:")
        self.stdout.write(f"   Name: {tenant.name}")
        self.stdout.write(f"   Subdomain: {tenant.subdomain}")
        self.stdout.write(f"   Admin Email: {tenant.admin_email}")
        self.stdout.write(f"   Max Users: {tenant.max_users}")
        self.stdout.write(f"   Multi-location: {'Yes' if tenant.supports_multi_location else 'No'}")
        
        if tenant.database_url:
            self.stdout.write(f"   Database: {tenant.database_url[:50]}...")
        else:
            self.stdout.write(f"   Database: {tenant.database_engine}")
            if tenant.database_host:
                self.stdout.write(f"   Host: {tenant.database_host}:{tenant.database_port or 'default'}")
        
        self.stdout.write(f"\n🔗 Access URL: http://{tenant.subdomain}.localhost:8000")
        
        if not options['skip_migrations']:
            self.stdout.write(f"\n👤 Default Login:")
            self.stdout.write(f"   Username: Akyen")
            self.stdout.write(f"   Password: 08000000")
            self.stdout.write(f"   Groups: Admin, Managers, Cashiers")
        
        self.stdout.write(f"\n📚 Next Steps:")
        if options['skip_migrations']:
            self.stdout.write(f"   1. Run: python manage.py migrate_tenant {tenant.subdomain}")
            self.stdout.write(f"   2. Access your tenant at the URL above")
        else:
            self.stdout.write(f"   1. Access your tenant at the URL above")
            self.stdout.write(f"   2. Login with the default credentials")
            self.stdout.write(f"   3. Create additional users and customize settings")
        
        self.stdout.write(f"\n🛠️  Management Commands:")
        self.stdout.write(f"   - View tenant: python manage.py setup_main_database")
        self.stdout.write(f"   - Reset database: python manage.py force_migrate_tenant {tenant.subdomain}")
        self.stdout.write(f"   - Manual setup: python manage.py manual_setup_tenant {tenant.subdomain}")
