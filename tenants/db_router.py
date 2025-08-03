from django.conf import settings
from .middleware import get_current_tenant


class TenantDatabaseRouter:
    """
    Database router that routes queries to tenant-specific databases.
    
    Routing Logic:
    - Tenant models (Tenant, TenantLocation) always use 'default' database
    - All other models use tenant-specific database when tenant is set
    - Falls back to 'default' database when no tenant context
    """
    
    # Apps that should always use the default database
    SHARED_APPS = ['tenants', 'admin', 'sessions']
    
    # Models that should always use the default database
    SHARED_MODELS = ['tenant', 'tenantlocation']
    
    def db_for_read(self, model, **hints):
        """Suggest the database to read from."""
        # Shared models always use default database
        if model._meta.app_label in self.SHARED_APPS:
            return 'default'
        
        if model._meta.model_name.lower() in self.SHARED_MODELS:
            return 'default'
        
        # For tenant-specific models, use tenant database
        tenant = get_current_tenant()
        if tenant:
            return tenant.database_name
        
        # Fallback to default database
        return 'default'
    
    def db_for_write(self, model, **hints):
        """Suggest the database to write to."""
        # Same logic as db_for_read
        return self.db_for_read(model, **hints)
    
    def allow_relation(self, obj1, obj2, **hints):
        """Allow relations if models are in the same database."""
        db_set = {'default'}
        
        # Add current tenant database if available
        tenant = get_current_tenant()
        if tenant:
            db_set.add(tenant.database_name)
        
        # Allow relations within the same database
        if obj1._state.db in db_set and obj2._state.db in db_set:
            return True
        
        return None
    
    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """Determine if migration should run on a database."""
        
        # Shared apps only migrate to default database
        if app_label in self.SHARED_APPS:
            return db == 'default'
        
        # Shared models only migrate to default database
        if model_name and model_name.lower() in self.SHARED_MODELS:
            return db == 'default'
        
        # Tenant-specific apps migrate to all tenant databases and default
        if db == 'default':
            # Allow migration to default for initial setup
            return True
        
        # Allow migration to tenant databases (check if db is a tenant database)
        from .utils import is_tenant_database
        if is_tenant_database(db):
            return True
        
        return False
    
    def get_tenant_database_config(self, tenant):
        """Generate database configuration for a tenant."""
        # In production, this would create separate database instances
        # For now, we'll use the same database with different names
        
        if hasattr(settings, 'TENANT_DATABASE_TEMPLATE'):
            # Use template configuration
            config = settings.TENANT_DATABASE_TEMPLATE.copy()
            config['NAME'] = tenant.database_name
            return config
        
        # Fallback configuration
        return {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': tenant.database_name,
            'USER': settings.DATABASES['default'].get('USER', ''),
            'PASSWORD': settings.DATABASES['default'].get('PASSWORD', ''),
            'HOST': settings.DATABASES['default'].get('HOST', ''),
            'PORT': settings.DATABASES['default'].get('PORT', ''),
            'OPTIONS': settings.DATABASES['default'].get('OPTIONS', {}),
        }
