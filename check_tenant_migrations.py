#!/usr/bin/env python3
"""
Check tenant database migrations
"""
import os
import sys
import django
from django.core.management import execute_from_command_line

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sales_management_project.settings')
django.setup()

from tenants.models import Tenant
import psycopg2

def check_tenant_migrations():
    # Get the tenant
    try:
        tenant = Tenant.objects.get(subdomain='render-test')
        print(f"✅ Tenant found: {tenant.name}")
        print(f"📍 Subdomain: {tenant.subdomain}")
        print(f"🗄️  Database URL: {tenant.database_url}")
        
        # Test connection to tenant database
        try:
            conn = psycopg2.connect(tenant.database_url, connect_timeout=10)
            print("✅ Connection to tenant database successful")
            
            # Check if tables exist
            cursor = conn.cursor()
            
            # Check for Django migration table
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'django_migrations'
                );
            """)
            has_migrations_table = cursor.fetchone()[0]
            print(f"📋 Django migrations table exists: {has_migrations_table}")
            
            if has_migrations_table:
                # Count migrations
                cursor.execute("SELECT COUNT(*) FROM django_migrations;")
                migration_count = cursor.fetchone()[0]
                print(f"📊 Total migrations applied: {migration_count}")
                
                # List applied migrations
                cursor.execute("SELECT app, name FROM django_migrations ORDER BY app, name;")
                migrations = cursor.fetchall()
                
                current_app = ""
                for app, name in migrations:
                    if app != current_app:
                        print(f"\n{app}:")
                        current_app = app
                    print(f"  ✅ {name}")
            
            # Check for auth_user table (should exist in tenant DB)
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'auth_user'
                );
            """)
            has_user_table = cursor.fetchone()[0]
            print(f"\n👤 Auth user table exists: {has_user_table}")
            
            if has_user_table:
                cursor.execute("SELECT COUNT(*) FROM auth_user;")
                user_count = cursor.fetchone()[0]
                print(f"👥 Users in tenant database: {user_count}")
                
                if user_count > 0:
                    cursor.execute("SELECT username, email, is_superuser FROM auth_user;")
                    users = cursor.fetchall()
                    for username, email, is_super in users:
                        role = "Superuser" if is_super else "User"
                        print(f"  👤 {username} ({email}) - {role}")
            
            cursor.close()
            conn.close()
            
        except Exception as e:
            print(f"❌ Error connecting to tenant database: {e}")
            
    except Tenant.DoesNotExist:
        print("❌ Tenant 'render-test' not found")
        
        # List all tenants
        tenants = Tenant.objects.all()
        print(f"\n📋 Available tenants ({tenants.count()}):")
        for t in tenants:
            print(f"  - {t.name} ({t.subdomain})")

if __name__ == "__main__":
    check_tenant_migrations()
