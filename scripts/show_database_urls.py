#!/usr/bin/env python
"""
Show where database URLs are stored in the multi-tenant system
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sales_management_project.settings')
django.setup()

from tenants.models import Tenant

def main():
    print("🗄️  DATABASE URL STORAGE EXPLANATION")
    print("="*80)
    print()
    
    print("📍 WHERE ARE DATABASE URLS STORED?")
    print("-" * 50)
    print("Database URLs are stored in the DJANGO DATABASE (NOT in environment files)")
    print()
    print("🏢 Main Database (db.sqlite3):")
    print("   ├── tenants_tenant table")
    print("   │   ├── database_url field (complete database URL)")
    print("   │   ├── database_engine field (e.g., django.db.backends.sqlite3)")
    print("   │   ├── database_name field (database name)")
    print("   │   ├── database_host field (database host)")
    print("   │   ├── database_port field (database port)")
    print("   │   ├── database_user field (database username)")
    print("   │   └── database_password field (database password)")
    print("   └── Other tenant metadata (name, subdomain, settings)")
    print()
    
    print("📁 FILE LOCATIONS:")
    print("-" * 30)
    print(f"Main database: {os.path.abspath('db.sqlite3')}")
    print(f"Tenant databases: {os.path.abspath('tenant_dbs/')}/*.sqlite3")
    print(f"Model definition: {os.path.abspath('tenants/models.py')}")
    print()
    
    print("🔍 CURRENT TENANT CONFIGURATIONS:")
    print("-" * 40)
    
    for tenant in Tenant.objects.all():
        print(f"Tenant: {tenant.name}")
        print(f"  📌 Subdomain: {tenant.subdomain}")
        print(f"  🔗 Database URL: {tenant.database_url or 'Not set (uses individual fields)'}")
        print(f"  🔧 Database Engine: {tenant.database_engine}")
        print(f"  📁 Database Name: {tenant.database_name}")
        print(f"  🖥️  Database Host: {tenant.database_host or 'Default'}")
        print(f"  🔌 Database Port: {tenant.database_port or 'Default'}")
        print(f"  👤 Database User: {tenant.database_user or 'Default'}")
        print(f"  🔒 Database Password: {'***' if tenant.database_password else 'Default'}")
        
        # Show the actual resolved configuration
        config = tenant.get_database_config()
        print(f"  ✅ Resolved Config: {config['ENGINE']} -> {config['NAME']}")
        print()
    
    print("="*80)
    print("📚 HOW IT WORKS:")
    print("="*80)
    print()
    print("1. 🏗️  TENANT CREATION:")
    print("   When you run: python manage.py shell")
    print("   Then execute: create_tenant(name='Demo', subdomain='demo')")
    print("   The tenant data is saved to the main database (db.sqlite3)")
    print()
    print("2. 🔄 RUNTIME DATABASE LOADING:")
    print("   When user visits: http://demo.localhost:8000")
    print("   ├── TenantMiddleware detects subdomain 'demo'")
    print("   ├── Looks up tenant in main database")
    print("   ├── Calls tenant.get_database_config()")
    print("   └── Dynamically loads tenant's database into Django settings")
    print()
    print("3. 💾 DATABASE URL PRIORITY:")
    print("   ├── First: Uses database_url field if provided")
    print("   ├── Second: Builds URL from individual fields")
    print("   └── Third: Falls back to default database settings")
    print()
    print("4. 🗂️  STORAGE SUMMARY:")
    print("   ├── Main DB (db.sqlite3): Tenant metadata + database configs")
    print("   ├── Tenant DBs (tenant_dbs/*.sqlite3): Actual tenant data")
    print("   └── Environment (.env): Only main database URL")

if __name__ == "__main__":
    main()
