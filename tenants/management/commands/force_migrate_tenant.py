#!/usr/bin/env python3
"""
Management command to force migrate a tenant database from scratch
"""
from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.conf import settings
from django.db import connections
from tenants.models import Tenant

class Command(BaseCommand):
    help = 'Force migrate tenant database from scratch'

    def add_arguments(self, parser):
        parser.add_argument(
            'subdomain',
            type=str,
            help='Subdomain of the tenant to migrate'
        )

    def handle(self, *args, **options):
        subdomain = options['subdomain']
        
        try:
            tenant = Tenant.objects.get(subdomain=subdomain)
        except Tenant.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'❌ Tenant with subdomain "{subdomain}" not found')
            )
            return
        
        self.stdout.write(f"🔄 Force migrating tenant: {tenant.name} ({tenant.subdomain})")
        self.stdout.write(f"   Database URL: {tenant.database_url}")
        
        try:
            # Use the tenant's own database configuration method
            db_config = tenant.get_database_config()
            
            # Add the tenant database to Django connections
            tenant_db_alias = f"tenant_{tenant.subdomain}"
            settings.DATABASES[tenant_db_alias] = db_config
            
            # Test connection
            test_conn = connections[tenant_db_alias]
            with test_conn.cursor() as cursor:
                cursor.execute("SELECT 1")
                
            self.stdout.write(f"✅ Connected to tenant database")
            
            # Clear migration history
            self.stdout.write("🗑️ Clearing migration history...")
            with test_conn.cursor() as cursor:
                # Drop django_migrations table to reset migration state
                cursor.execute("DROP TABLE IF EXISTS django_migrations CASCADE")
                
            # Run migrations with --run-syncdb to create all tables
            self.stdout.write("📦 Running full database sync...")
            
            # Ensure the connection is properly configured
            test_conn.ensure_connection()
            
            # Set autocommit to True to ensure changes are committed
            test_conn.connection.autocommit = True
            
            call_command(
                'migrate',
                database=tenant_db_alias,
                run_syncdb=True,
                verbosity=2
            )
            
            # Force commit any pending transactions
            test_conn.connection.commit()
            
            # Verify tables were created
            with test_conn.cursor() as cursor:
                cursor.execute("""
                    SELECT table_name FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    ORDER BY table_name
                """)
                tables = cursor.fetchall()
                self.stdout.write(f"✅ Created {len(tables)} tables: {[t[0] for t in tables[:5]]}{'...' if len(tables) > 5 else ''}")
            
            # Create default superuser manually
            self.stdout.write("👤 Creating default superuser...")
            self.create_superuser_direct(tenant_db_alias)
            
            self.stdout.write(
                self.style.SUCCESS(f'✅ Force migration completed for tenant: {tenant.name}')
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error force migrating tenant database: {e}')
            )
    
    def create_superuser_direct(self, database_alias):
        """Create superuser using direct SQL to avoid Django ORM issues"""
        from django.db import connections
        import hashlib
        
        try:
            conn = connections[database_alias]
            with conn.cursor() as cursor:
                # Create groups first
                cursor.execute("""
                    INSERT INTO auth_group (name) VALUES ('Managers') 
                    ON CONFLICT (name) DO NOTHING
                """)
                cursor.execute("""
                    INSERT INTO auth_group (name) VALUES ('Sales Team') 
                    ON CONFLICT (name) DO NOTHING
                """)
                
                # Check if user exists
                cursor.execute("SELECT id FROM auth_user WHERE username = %s", ['Akyen'])
                if not cursor.fetchone():
                    # Create superuser using Django's password hashing
                    from django.contrib.auth.hashers import make_password
                    password_hash = make_password('08000000')
                    
                    cursor.execute("""
                        INSERT INTO auth_user 
                        (username, email, first_name, last_name, is_staff, is_active, is_superuser, password, date_joined)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW())
                    """, [
                        'Akyen',
                        'admin@company.com', 
                        'System',
                        'Administrator',
                        True,
                        True,
                        True,
                        password_hash
                    ])
                    
                    # Get user ID and manager group ID
                    cursor.execute("SELECT id FROM auth_user WHERE username = %s", ['Akyen'])
                    user_id = cursor.fetchone()[0]
                    
                    cursor.execute("SELECT id FROM auth_group WHERE name = %s", ['Managers'])
                    group_id = cursor.fetchone()[0]
                    
                    # Add user to manager group
                    cursor.execute("""
                        INSERT INTO auth_user_groups (user_id, group_id) VALUES (%s, %s)
                        ON CONFLICT DO NOTHING
                    """, [user_id, group_id])
                    
                    self.stdout.write(f"   ✅ Created superuser: Akyen (password: 08000000)")
                else:
                    self.stdout.write(f"   ℹ️ Superuser 'Akyen' already exists")
                    
        except Exception as e:
            self.stdout.write(f"   ⚠️ Error creating superuser: {e}")
