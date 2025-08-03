"""
Utility functions for tenant operations and management.
"""

from django.conf import settings
from django.db import connections
from django.db import models
from .models import Tenant
from .middleware import get_current_tenant


def get_tenant_database_key(tenant=None):
    """
    Get the database key for a tenant.
    
    Args:
        tenant: Tenant instance. If None, uses current tenant from middleware.
        
    Returns:
        str: Database key for the tenant, or 'default' if no tenant.
    """
    if tenant is None:
        tenant = get_current_tenant()
    
    if tenant:
        return tenant.database_name
    return 'default'


def ensure_tenant_database_exists(tenant):
    """
    Ensure the tenant's database exists in Django's database configuration.
    
    Args:
        tenant: Tenant instance
        
    Returns:
        bool: True if database exists or was created, False otherwise
    """
    if tenant.database_name in settings.DATABASES:
        return True
    
    # Generate database configuration for tenant
    from .db_router import TenantDatabaseRouter
    router = TenantDatabaseRouter()
    config = router.get_tenant_database_config(tenant)
    
    # Add to Django settings
    settings.DATABASES[tenant.database_name] = config
    
    return True


def get_tenant_connection(tenant=None):
    """
    Get database connection for a tenant.
    
    Args:
        tenant: Tenant instance. If None, uses current tenant.
        
    Returns:
        Database connection for the tenant
    """
    if tenant is None:
        tenant = get_current_tenant()
    
    if tenant:
        ensure_tenant_database_exists(tenant)
        return connections[tenant.database_name]
    
    return connections['default']


def switch_tenant_context(tenant):
    """
    Context manager to temporarily switch tenant context.
    
    Usage:
        with switch_tenant_context(some_tenant):
            # Operations here use some_tenant's database
            invoices = Invoice.objects.all()
    """
    from .middleware import set_current_tenant
    
    class TenantContext:
        def __init__(self, new_tenant):
            self.new_tenant = new_tenant
            self.original_tenant = None
        
        def __enter__(self):
            self.original_tenant = get_current_tenant()
            set_current_tenant(self.new_tenant)
            return self
        
        def __exit__(self, exc_type, exc_val, exc_tb):
            set_current_tenant(self.original_tenant)
    
    return TenantContext(tenant)


def get_all_tenant_databases():
    """
    Get list of all tenant database names.
    
    Returns:
        list: List of tenant database names
    """
    return list(Tenant.objects.values_list('database_name', flat=True))


def is_tenant_database(database_name):
    """
    Check if a database name belongs to a tenant.
    
    Args:
        database_name: Name of the database
        
    Returns:
        bool: True if database belongs to a tenant
    """
    return Tenant.objects.filter(database_name=database_name).exists()


def validate_tenant_subdomain(subdomain):
    """
    Validate tenant subdomain format.
    
    Args:
        subdomain: Subdomain to validate
        
    Returns:
        tuple: (is_valid, error_message)
    """
    import re
    
    if not subdomain:
        return False, "Subdomain cannot be empty"
    
    if len(subdomain) > 63:
        return False, "Subdomain cannot be longer than 63 characters"
    
    if not re.match(r'^[a-z0-9]([a-z0-9\-]{0,61}[a-z0-9])?$', subdomain):
        return False, "Subdomain must contain only lowercase letters, numbers, and hyphens"
    
    # Check for reserved subdomains
    reserved = ['www', 'admin', 'api', 'mail', 'ftp', 'localhost']
    if subdomain in reserved:
        return False, f"'{subdomain}' is a reserved subdomain"
    
    # Check if subdomain already exists
    if Tenant.objects.filter(subdomain=subdomain).exists():
        return False, f"Subdomain '{subdomain}' is already taken"
    
    return True, ""


def get_tenant_summary():
    """
    Get summary statistics for all tenants.
    
    Returns:
        dict: Summary statistics
    """
    tenants = Tenant.objects.all()
    
    return {
        'total_tenants': tenants.count(),
        'active_tenants': tenants.filter(is_active=True).count(),
        'inactive_tenants': tenants.filter(is_active=False).count(),
        'multi_location_tenants': tenants.filter(supports_multi_location=True).count(),
        'single_location_tenants': tenants.filter(supports_multi_location=False).count(),
        'total_max_users': tenants.aggregate(
            total=models.Sum('max_users')
        )['total'] or 0,
    }


def ensure_tenant_database_loaded(tenant):
    """Ensure tenant's database configuration is loaded in Django settings"""
    if tenant and tenant.database_name not in settings.DATABASES:
        database_config = tenant.get_database_config()
        settings.DATABASES[tenant.database_name] = database_config
        
        # Create database directory for SQLite if needed
        if 'sqlite3' in database_config.get('ENGINE', ''):
            import os
            db_path = database_config['NAME']
            db_dir = os.path.dirname(db_path)
            if db_dir and not os.path.exists(db_dir):
                os.makedirs(db_dir, exist_ok=True)


def load_all_tenant_databases():
    """Load all tenant databases into Django settings (useful for startup)"""
    for tenant in Tenant.objects.filter(is_active=True):
        ensure_tenant_database_loaded(tenant)
