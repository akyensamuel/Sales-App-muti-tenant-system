#!/usr/bin/env python
"""
Setup script to create and migrate tenant databases
"""

import os
import django
import sys

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sales_management_project.settings')

# Change to the project directory
project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(project_dir)
sys.path.insert(0, project_dir)

django.setup()

from tenants.models import Tenant
from tenants.utils import ensure_tenant_database_loaded
from django.conf import settings
from django.core.management import call_command
from django.db import connections


def setup_tenant_databases():
    """Setup all tenant databases"""
    
    print("🔧 Setting up tenant databases...\n")
    
    tenants = Tenant.objects.all()
    
    if not tenants.exists():
        print("No tenants found. Create some tenants first!")
        return
    
    for tenant in tenants:
        print(f"Setting up database for: {tenant.name}")
        print(f"  Subdomain: {tenant.subdomain}")
        
        # Ensure database configuration is loaded
        ensure_tenant_database_loaded(tenant)
        
        db_config = settings.DATABASES[tenant.database_name]
        print(f"  Database: {db_config['NAME']}")
        
        try:
            # Test connection and run migrations
            connection = connections[tenant.database_name]
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
            
            print("  Running migrations...")
            call_command('migrate', database=tenant.database_name, verbosity=0)
            print("  ✅ Database setup complete!")
            
        except Exception as e:
            print(f"  ❌ Error setting up database: {e}")
        
        print()


def show_database_info():
    """Show information about all configured databases"""
    
    print("📊 Database Configuration Summary\n")
    
    print("Configured Databases:")
    for db_name, db_config in settings.DATABASES.items():
        print(f"  • {db_name}")
        print(f"    Engine: {db_config.get('ENGINE', 'Unknown')}")
        print(f"    Location: {db_config.get('NAME', 'Unknown')}")
        
        # Check if database file exists (for SQLite)
        if 'sqlite3' in db_config.get('ENGINE', ''):
            db_path = db_config.get('NAME', '')
            if os.path.exists(db_path):
                size = os.path.getsize(db_path)
                print(f"    Status: ✅ Exists ({size:,} bytes)")
            else:
                print(f"    Status: ❌ File not found")
        print()


if __name__ == '__main__':
    print("🏢 Multi-Tenant Database Setup\n")
    
    # Load all tenant databases into Django settings
    print("Loading tenant database configurations...")
    for tenant in Tenant.objects.all():
        ensure_tenant_database_loaded(tenant)
    
    # Show current configuration
    show_database_info()
    
    # Setup databases
    setup_tenant_databases()
    
    # Show final status
    print("="*60)
    print("Final Database Status:")
    show_database_info()
    
    print("🎉 Setup complete!")
    print("\nTo access tenants locally:")
    for tenant in Tenant.objects.all():
        print(f"  • {tenant.name}: http://{tenant.subdomain}.localhost:8000")
