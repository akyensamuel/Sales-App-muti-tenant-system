#!/usr/bin/env python3
"""
Management command to delete a tenant and all associated data
"""
from django.core.management.base import BaseCommand, CommandError
from tenants.models import Tenant
from django.conf import settings
import os
import logging
from datetime import datetime


class Command(BaseCommand):
    help = 'Delete a tenant and all associated data'

    def add_arguments(self, parser):
        parser.add_argument('subdomain', type=str, help='Tenant subdomain to delete')
        parser.add_argument(
            '--force',
            action='store_true',
            help='Skip confirmation prompt'
        )
        parser.add_argument(
            '--keep-database',
            action='store_true',
            help='Keep the tenant database (only remove from main database)'
        )

    def handle(self, *args, **options):
        subdomain = options['subdomain']
        force = options['force']
        keep_database = options['keep_database']

        self.stdout.write(self.style.HTTP_INFO('🗑️  Tenant Deletion Process'))
        self.stdout.write('=' * 50)

        try:
            # Find the tenant
            try:
                tenant = Tenant.objects.get(subdomain=subdomain)
            except Tenant.DoesNotExist:
                raise CommandError(f"❌ Tenant with subdomain '{subdomain}' does not exist")

            # Display tenant information
            self.show_tenant_info(tenant)

            # Confirmation prompt (unless force is used)
            if not force:
                if not self.confirm_deletion(tenant):
                    self.stdout.write(self.style.WARNING('🚫 Deletion cancelled by user'))
                    return

            # Log the deletion attempt
            self.log_tenant_operation('DELETE_START', tenant)

            # Delete tenant database (if not keeping it)
            if not keep_database:
                self.delete_tenant_database(tenant)
            else:
                self.stdout.write(self.style.WARNING('⚠️  Keeping tenant database as requested'))

            # Remove tenant from main database
            self.delete_tenant_record(tenant)

            # Log successful deletion
            self.log_tenant_operation('DELETE_SUCCESS', tenant)

            # Show success message
            self.show_success_message(tenant, keep_database)

        except Exception as e:
            # Log the error
            if 'tenant' in locals():
                self.log_tenant_operation('DELETE_ERROR', tenant, str(e))
            
            self.stdout.write(self.style.ERROR(f'❌ Error deleting tenant: {e}'))
            raise CommandError(str(e))

    def show_tenant_info(self, tenant):
        """Display detailed tenant information"""
        self.stdout.write(f"\n📋 Tenant Information:")
        self.stdout.write(f"   Name: {tenant.name}")
        self.stdout.write(f"   Subdomain: {tenant.subdomain}")
        self.stdout.write(f"   Database: {tenant.database_name}")
        self.stdout.write(f"   Admin Email: {tenant.admin_email}")
        self.stdout.write(f"   Max Users: {tenant.max_users}")
        self.stdout.write(f"   Multi-location: {'Yes' if tenant.supports_multi_location else 'No'}")
        
        if tenant.database_url:
            # Mask sensitive parts of the URL
            masked_url = self.mask_database_url(tenant.database_url)
            self.stdout.write(f"   Database URL: {masked_url}")
        else:
            self.stdout.write(f"   Database Host: {tenant.database_host or 'Auto-configured'}")
        
        self.stdout.write(f"   Created: {tenant.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
        self.stdout.write(f"   Access URL: http://{tenant.subdomain}.localhost:8000/")

    def mask_database_url(self, url):
        """Mask sensitive information in database URL"""
        import re
        # Replace password with asterisks
        return re.sub(r'://([^:]+):([^@]+)@', r'://\1:****@', url)

    def confirm_deletion(self, tenant):
        """Ask user for confirmation"""
        self.stdout.write(f"\n⚠️  WARNING: This will permanently delete:")
        self.stdout.write(f"   • Tenant record from main database")
        self.stdout.write(f"   • All tenant database data (users, sales, accounting)")
        self.stdout.write(f"   • Database: {tenant.database_name}")
        if tenant.database_url and 'render' in tenant.database_url.lower():
            self.stdout.write(f"   • External database on Render/Cloud provider")
        
        self.stdout.write(f"\n🚨 This action CANNOT be undone!")
        
        response = input(f"\nType 'DELETE {tenant.subdomain}' to confirm deletion: ")
        
        return response == f'DELETE {tenant.subdomain}'

    def delete_tenant_database(self, tenant):
        """Delete or warn about tenant database"""
        self.stdout.write(f"\n🗄️  Handling tenant database...")
        
        if tenant.database_url:
            # External database - warn user
            if any(provider in tenant.database_url.lower() for provider in ['render', 'aws', 'google', 'azure']):
                self.stdout.write(self.style.WARNING(
                    f"⚠️  External database detected: {self.mask_database_url(tenant.database_url)}"
                ))
                self.stdout.write(self.style.WARNING(
                    "   Database is hosted externally and must be deleted manually"
                ))
                self.stdout.write(self.style.WARNING(
                    "   from your cloud provider (Render, AWS, etc.)"
                ))
            else:
                self.stdout.write(f"📡 External database: {self.mask_database_url(tenant.database_url)}")
        else:
            # Local SQLite database
            if 'sqlite3' in tenant.database_engine:
                db_path = f"{settings.BASE_DIR}/tenant_dbs/{tenant.database_name}.sqlite3"
                if os.path.exists(db_path):
                    try:
                        os.remove(db_path)
                        self.stdout.write(self.style.SUCCESS(f"✅ Deleted local database file: {db_path}"))
                    except Exception as e:
                        self.stdout.write(self.style.WARNING(f"⚠️  Could not delete database file: {e}"))
                else:
                    self.stdout.write(f"ℹ️  Database file not found: {db_path}")
            else:
                self.stdout.write(f"📊 Database configured but location unknown: {tenant.database_name}")

    def delete_tenant_record(self, tenant):
        """Remove tenant record from main database"""
        self.stdout.write(f"\n🗑️  Removing tenant from main database...")
        
        # Store info for logging before deletion
        tenant_info = {
            'name': tenant.name,
            'subdomain': tenant.subdomain,
            'database_name': tenant.database_name,
            'admin_email': tenant.admin_email
        }
        
        # Delete the tenant record
        tenant.delete()
        
        self.stdout.write(self.style.SUCCESS(f"✅ Tenant '{tenant_info['name']}' removed from main database"))

    def log_tenant_operation(self, operation, tenant, error_msg=None):
        """Log tenant operations to local file"""
        # Ensure logs directory exists
        logs_dir = os.path.join(settings.BASE_DIR, 'logs')
        os.makedirs(logs_dir, exist_ok=True)
        
        # Set up logging
        log_file = os.path.join(logs_dir, 'tenant_operations.log')
        
        # Configure logger
        logger = logging.getLogger('tenant_operations')
        logger.setLevel(logging.INFO)
        
        # Remove existing handlers to avoid duplicates
        logger.handlers.clear()
        
        # Create file handler
        handler = logging.FileHandler(log_file, mode='a', encoding='utf-8')
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        # Create log entry
        timestamp = datetime.now().isoformat()
        
        if operation == 'DELETE_START':
            log_message = (
                f"TENANT_DELETE_START | "
                f"Subdomain: {tenant.subdomain} | "
                f"Name: {tenant.name} | "
                f"Database: {tenant.database_name} | "
                f"Admin: {tenant.admin_email} | "
                f"Database_URL: {self.mask_database_url(tenant.database_url) if tenant.database_url else 'N/A'} | "
                f"Access_URL: http://{tenant.subdomain}.localhost:8000/"
            )
        elif operation == 'DELETE_SUCCESS':
            log_message = (
                f"TENANT_DELETE_SUCCESS | "
                f"Subdomain: {tenant.subdomain} | "
                f"Name: {tenant.name} | "
                f"Deletion completed successfully"
            )
        elif operation == 'DELETE_ERROR':
            log_message = (
                f"TENANT_DELETE_ERROR | "
                f"Subdomain: {tenant.subdomain} | "
                f"Name: {tenant.name} | "
                f"Error: {error_msg}"
            )
        
        logger.info(log_message)
        
        # Clean up handler
        handler.close()
        logger.removeHandler(handler)

    def show_success_message(self, tenant, keep_database):
        """Display success message"""
        self.stdout.write(self.style.SUCCESS('\n🎉 TENANT DELETED SUCCESSFULLY!'))
        self.stdout.write('=' * 50)
        
        self.stdout.write(f"\n📋 Deletion Summary:")
        self.stdout.write(f"   • Tenant '{tenant.name}' removed from main database ✅")
        
        if keep_database:
            self.stdout.write(f"   • Tenant database preserved (--keep-database flag) ⚠️")
        else:
            if tenant.database_url and any(provider in tenant.database_url.lower() for provider in ['render', 'aws', 'google', 'azure']):
                self.stdout.write(f"   • External database requires manual deletion ⚠️")
            else:
                self.stdout.write(f"   • Local database files removed ✅")
        
        self.stdout.write(f"   • Operation logged to logs/tenant_operations.log ✅")
        
        self.stdout.write(f"\n🚨 Important Notes:")
        self.stdout.write(f"   • Subdomain '{tenant.subdomain}' is now available for reuse")
        self.stdout.write(f"   • All URLs for this tenant are now invalid")
        
        if tenant.database_url and any(provider in tenant.database_url.lower() for provider in ['render', 'aws', 'google', 'azure']):
            self.stdout.write(f"   • Remember to delete the external database manually")
            self.stdout.write(f"   • Database URL: {self.mask_database_url(tenant.database_url)}")
