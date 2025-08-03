#!/usr/bin/env python3
"""
Management command to manually create tenant database tables using raw SQL
"""
from django.core.management.base import BaseCommand
from django.conf import settings
from django.db import connections
from tenants.models import Tenant

class Command(BaseCommand):
    help = 'Manually create tenant database tables using raw SQL'

    def add_arguments(self, parser):
        parser.add_argument(
            'subdomain',
            type=str,
            help='Subdomain of the tenant to set up'
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
        
        self.stdout.write(f"🔄 Creating tables manually for: {tenant.name} ({tenant.subdomain})")
        
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
            
            # Create tables manually using raw SQL
            self.create_auth_tables(tenant_db_alias)
            self.create_basic_tables(tenant_db_alias)
            self.create_superuser(tenant_db_alias)
            
            self.stdout.write(
                self.style.SUCCESS(f'✅ Manual table creation completed for: {tenant.name}')
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error creating tables manually: {e}')
            )
    
    def create_auth_tables(self, database_alias):
        """Create essential auth tables using raw SQL"""
        conn = connections[database_alias]
        
        sql_commands = [
            # Content types table
            """
            CREATE TABLE IF NOT EXISTS django_content_type (
                id SERIAL PRIMARY KEY,
                app_label VARCHAR(100) NOT NULL,
                model VARCHAR(100) NOT NULL,
                UNIQUE(app_label, model)
            );
            """,
            
            # Auth permission table
            """
            CREATE TABLE IF NOT EXISTS auth_permission (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                content_type_id INTEGER NOT NULL,
                codename VARCHAR(100) NOT NULL,
                UNIQUE(content_type_id, codename)
            );
            """,
            
            # Auth group table
            """
            CREATE TABLE IF NOT EXISTS auth_group (
                id SERIAL PRIMARY KEY,
                name VARCHAR(150) UNIQUE NOT NULL
            );
            """,
            
            # Auth user table
            """
            CREATE TABLE IF NOT EXISTS auth_user (
                id SERIAL PRIMARY KEY,
                password VARCHAR(128) NOT NULL,
                last_login TIMESTAMP WITH TIME ZONE,
                is_superuser BOOLEAN NOT NULL,
                username VARCHAR(150) UNIQUE NOT NULL,
                first_name VARCHAR(150) NOT NULL,
                last_name VARCHAR(150) NOT NULL,
                email VARCHAR(254) NOT NULL,
                is_staff BOOLEAN NOT NULL,
                is_active BOOLEAN NOT NULL,
                date_joined TIMESTAMP WITH TIME ZONE NOT NULL
            );
            """,
            
            # Auth user groups many-to-many table
            """
            CREATE TABLE IF NOT EXISTS auth_user_groups (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL,
                group_id INTEGER NOT NULL,
                UNIQUE(user_id, group_id)
            );
            """,
            
            # Sessions table
            """
            CREATE TABLE IF NOT EXISTS django_session (
                session_key VARCHAR(40) PRIMARY KEY,
                session_data TEXT NOT NULL,
                expire_date TIMESTAMP WITH TIME ZONE NOT NULL
            );
            """
        ]
        
        with conn.cursor() as cursor:
            for sql in sql_commands:
                self.stdout.write(f"   📦 Creating table...")
                cursor.execute(sql)
                
        self.stdout.write(f"✅ Auth tables created")
    
    def create_basic_tables(self, database_alias):
        """Create basic sales app tables"""
        conn = connections[database_alias]
        
        sql_commands = [
            # Basic sales table
            """
            CREATE TABLE IF NOT EXISTS sales_app_customer (
                id SERIAL PRIMARY KEY,
                name VARCHAR(200) NOT NULL,
                email VARCHAR(254),
                phone VARCHAR(20),
                address TEXT,
                created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
            );
            """,
            
            # Basic product table
            """
            CREATE TABLE IF NOT EXISTS sales_app_product (
                id SERIAL PRIMARY KEY,
                name VARCHAR(200) NOT NULL,
                description TEXT,
                price DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
                stock_quantity INTEGER NOT NULL DEFAULT 0,
                created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
            );
            """
        ]
        
        with conn.cursor() as cursor:
            for sql in sql_commands:
                cursor.execute(sql)
                
        self.stdout.write(f"✅ Basic tables created")
    
    def create_superuser(self, database_alias):
        """Create superuser using raw SQL"""
        conn = connections[database_alias]
        
        from django.contrib.auth.hashers import make_password
        password_hash = make_password('08000000')
        
        with conn.cursor() as cursor:
            # Insert default groups
            cursor.execute("""
                INSERT INTO auth_group (name) VALUES ('Admin') 
                ON CONFLICT (name) DO NOTHING
            """)
            cursor.execute("""
                INSERT INTO auth_group (name) VALUES ('Managers') 
                ON CONFLICT (name) DO NOTHING
            """)
            cursor.execute("""
                INSERT INTO auth_group (name) VALUES ('Cashiers') 
                ON CONFLICT (name) DO NOTHING
            """)
            
            # Check if user exists
            cursor.execute("SELECT id FROM auth_user WHERE username = %s", ['Akyen'])
            if not cursor.fetchone():
                # Create superuser
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
                
                # Get user ID and Admin group ID
                cursor.execute("SELECT id FROM auth_user WHERE username = %s", ['Akyen'])
                user_id = cursor.fetchone()[0]
                
                cursor.execute("SELECT id FROM auth_group WHERE name = %s", ['Admin'])
                group_result = cursor.fetchone()
                if group_result:
                    group_id = group_result[0]
                    
                    # Add user to Admin group
                    cursor.execute("""
                        INSERT INTO auth_user_groups (user_id, group_id) VALUES (%s, %s)
                        ON CONFLICT DO NOTHING
                    """, [user_id, group_id])
                
                self.stdout.write(f"✅ Created superuser: Akyen (password: 08000000)")
            else:
                self.stdout.write(f"ℹ️ Superuser 'Akyen' already exists")
