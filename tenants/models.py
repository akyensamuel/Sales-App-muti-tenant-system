from django.db import models
from django.core.validators import RegexValidator
from django.utils import timezone


class Tenant(models.Model):
    """
    Represents an organization/tenant in the multi-tenant system.
    Each tenant gets its own database and subdomain.
    """
    
    # Tenant identification
    name = models.CharField(
        max_length=100, 
        unique=True,
        help_text="Organization name (e.g., 'ABC Company')"
    )
    
    subdomain = models.CharField(
        max_length=63,
        unique=True,
        validators=[
            RegexValidator(
                regex=r'^[a-z0-9]([a-z0-9\-]{0,61}[a-z0-9])?$',
                message='Subdomain must be lowercase letters, numbers, and hyphens only'
            )
        ],
        help_text="Subdomain for tenant (e.g., 'abc' for abc.yourapp.com)"
    )
    
    # Database configuration
    database_name = models.CharField(
        max_length=63,
        unique=True,
        help_text="Database name for this tenant"
    )
    
    # Advanced database configuration (optional)
    database_url = models.URLField(
        blank=True,
        null=True,
        help_text="Complete database URL (overrides other settings if provided)"
    )
    
    database_engine = models.CharField(
        max_length=50,
        default='django.db.backends.postgresql',
        help_text="Database engine (e.g., django.db.backends.sqlite3)"
    )
    
    database_host = models.CharField(
        max_length=255,
        blank=True,
        default='',
        help_text="Database host (leave empty to use default)"
    )
    
    database_port = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Database port (leave empty to use default)"
    )
    
    database_user = models.CharField(
        max_length=100,
        blank=True,
        default='',
        help_text="Database username (leave empty to use default)"
    )
    
    database_password = models.CharField(
        max_length=100,
        blank=True,
        default='',
        help_text="Database password (leave empty to use default)"
    )
    
    # Tenant metadata
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this tenant is active and accessible"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Contact information
    admin_email = models.EmailField(
        help_text="Primary admin email for this organization"
    )
    
    # Tenant settings
    max_users = models.PositiveIntegerField(
        default=50,
        help_text="Maximum number of users allowed for this tenant"
    )
    
    # Location tracking support
    supports_multi_location = models.BooleanField(
        default=True,
        help_text="Whether this tenant uses multiple locations"
    )
    
    class Meta:
        ordering = ['name']
        verbose_name = 'Tenant'
        verbose_name_plural = 'Tenants'
    
    def __str__(self):
        return f"{self.name} ({self.subdomain})"
    
    @property
    def full_domain(self):
        """Return the full domain for this tenant"""
        # In production, this would be something like: f"{self.subdomain}.yoursalesapp.com"
        return f"{self.subdomain}.localhost:8000"  # For local development
    
    def get_database_config(self):
        """Generate database configuration for this tenant"""
        from django.conf import settings
        import dj_database_url
        
        # If database_url is provided, parse and use it
        if self.database_url:
            try:
                config = dj_database_url.parse(self.database_url)
                
                # Start with default database settings to ensure all required keys are present
                from django.conf import settings
                default_config = settings.DATABASES['default'].copy()
                
                # Update with parsed URL config
                default_config.update(config)
                
                # Ensure OPTIONS key exists with default value
                if 'OPTIONS' not in default_config:
                    default_config['OPTIONS'] = {}
                
                # Ensure all required keys exist
                default_config.setdefault('CONN_MAX_AGE', 0)
                default_config.setdefault('AUTOCOMMIT', True)
                default_config.setdefault('ATOMIC_REQUESTS', False)
                
                return default_config
            except Exception as e:
                print(f"Error parsing database URL: {e}")
                # Fall back to manual configuration
        
        # Start with a copy of the default database configuration
        # This ensures all required Django database settings are present
        config = settings.DATABASES['default'].copy()
        
        # Override with tenant-specific settings
        config['ENGINE'] = self.database_engine
        config['NAME'] = self.database_name
        
        if self.database_host:
            config['HOST'] = self.database_host
        if self.database_port:
            config['PORT'] = self.database_port
        if self.database_user:
            config['USER'] = self.database_user
        if self.database_password:
            config['PASSWORD'] = self.database_password
        
        # Special handling for SQLite
        if 'sqlite3' in self.database_engine:
            from django.conf import settings
            # For SQLite, use full path and remove network-related settings
            if not self.database_name.endswith('.sqlite3'):
                config['NAME'] = f"{settings.BASE_DIR}/tenant_dbs/{self.database_name}.sqlite3"
            
            # Remove network-related settings for SQLite
            config.pop('HOST', None)
            config.pop('PORT', None)
            config.pop('USER', None)
            config.pop('PASSWORD', None)
        
        return config
    
    def save(self, *args, **kwargs):
        """Auto-generate database name from subdomain if not provided"""
        if not self.database_name:
            self.database_name = f"sales_{self.subdomain}"
        
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        # Set up tenant database and default data if this is a new tenant
        if is_new:
            self.setup_tenant_database()
    
    def setup_tenant_database(self):
        """Set up tenant database with migrations and default data"""
        from django.core.management import call_command
        from .utils import ensure_tenant_database_loaded
        from .middleware import set_current_tenant
        import os
        
        try:
            print(f"🔧 Setting up tenant database for {self.name}...")
            
            # Check if this is a remote database URL that we can't actually connect to in development
            if self.database_url and ('postgresql://' in self.database_url or 'mysql://' in self.database_url):
                print(f"   📡 Remote database URL detected: {self.database_url}")
                print(f"   ⚠️  Database setup skipped - remote database configuration saved.")
                print(f"   📝 In production, ensure the database exists and is accessible.")
                print(f"   🚀 Run migrations manually in production: python manage.py migrate --database={self.database_name}")
                return
            
            # Ensure tenant database is loaded in Django settings
            ensure_tenant_database_loaded(self)
            
            # Set current tenant context
            set_current_tenant(self)
            
            # Run migrations for all necessary apps
            apps_to_migrate = ['contenttypes', 'auth', 'sales_app', 'accounting_app']
            
            for app in apps_to_migrate:
                print(f"   Migrating {app} to {self.database_name}...")
                call_command('migrate', app, database=self.database_name, verbosity=0)
            
            # Create default groups and superuser
            self.create_default_groups_and_user()
            
            print(f"✅ Tenant database setup completed for {self.name}")
            
        except Exception as e:
            error_msg = str(e).lower()
            if ('could not connect' in error_msg or 
                'connection refused' in error_msg or
                'mysqldb module' in error_msg or
                'psycopg2' in error_msg or
                'no such host' in error_msg):
                print(f"   📡 Remote/external database detected")
                print(f"   💾 Database configuration saved successfully")
                print(f"   📝 In production:")
                print(f"      1. Ensure database server is accessible")
                print(f"      2. Install required database drivers (psycopg2/mysqlclient)")
                print(f"      3. Run: python manage.py migrate --database={self.database_name}")
                print(f"      4. Run: python manage.py create_tenant_admins")
            else:
                print(f"❌ Error setting up tenant database for {self.name}: {str(e)}")
                raise
        finally:
            # Clear tenant context
            set_current_tenant(None)
    
    def create_default_groups_and_user(self):
        """Create default groups and superuser for the tenant"""
        from django.contrib.auth.models import User, Group
        
        # Create default groups
        default_groups = ['Admin', 'Managers', 'Cashiers']
        
        for group_name in default_groups:
            group, created = Group.objects.using(self.database_name).get_or_create(
                name=group_name
            )
            if created:
                print(f"   ✓ Created group: {group_name}")
        
        # Create default superuser
        username = "Akyen"
        email = "lordsades1@gmail.com"
        password = "08000000"
        
        try:
            # Check if user already exists
            User.objects.using(self.database_name).get(username=username)
            print(f"   ⚠️  Superuser {username} already exists")
        except User.DoesNotExist:
            # Create the superuser
            user = User(
                username=username,
                email=email,
                is_staff=True,
                is_superuser=True,
                first_name="Akyen",
                last_name="Samuel"
            )
            user.set_password(password)
            user.save(using=self.database_name)
            
            # Add to ALL required groups (Admin, Managers, Cashiers)
            for group_name in default_groups:
                group = Group.objects.using(self.database_name).get(name=group_name)
                user.groups.add(group)
                print(f"   ✅ Added user to group: {group_name}")
            
            user.save(using=self.database_name)
            
            print(f"   ✅ Created superuser: {username} (password: {password})")
            print(f"   📧 Email: {email}")
            print(f"   👥 Groups: {', '.join(default_groups)}")
            print(f"   🔗 Access: http://{self.subdomain}.localhost:8000/accounting/")


class TenantLocation(models.Model):
    """
    Represents a physical location within a tenant organization.
    Used for multi-location performance tracking.
    """
    
    tenant = models.ForeignKey(
        Tenant, 
        on_delete=models.CASCADE, 
        related_name='locations'
    )
    
    name = models.CharField(
        max_length=100,
        help_text="Location name (e.g., 'Downtown Store', 'Warehouse A')"
    )
    
    code = models.CharField(
        max_length=10,
        help_text="Short code for location (e.g., 'DT', 'WH1')"
    )
    
    address = models.TextField(blank=True)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = [['tenant', 'code'], ['tenant', 'name']]
        ordering = ['tenant', 'name']
    
    def __str__(self):
        return f"{self.tenant.name} - {self.name}"
