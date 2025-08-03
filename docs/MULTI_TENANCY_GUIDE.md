# 🏢 Multi-Tenancy Implementation Guide

## Overview

This document describes the multi-tenancy implementation for this Sales Management Project. The system supports multiple organizations (tenants) with complete database isolation and subdomain-based routing.

## 🏗️ Architecture

### Tenancy Model: **Database-Level Multi-Tenancy**
- Each organization gets its own separate database
- Complete data isolation between tenants
- Shared application code and infrastructure
- Subdomain-based tenant identification

### URL Structure
```
org1.yourapp.com → Organization 1 (Database: sales_org1)
org2.yourapp.com → Organization 2 (Database: sales_org2)
demo.yourapp.com → Demo Organization (Database: sales_demo)
admin.yourapp.com → Admin Interface (Database: default)
```

## 🔧 Implementation Components

### 1. Tenant Models (`tenants/models.py`)
- **Tenant**: Core organization model with subdomain and database configuration
- **TenantLocation**: Support for multi-location organizations

### 2. Tenant Middleware (`tenants/middleware.py`)
- Detects tenant from subdomain
- Sets current tenant context for request
- Handles tenant-not-found scenarios

### 3. Database Router (`tenants/db_router.py`)
- Routes queries to appropriate tenant database
- Handles shared vs tenant-specific models
- Manages migration routing

### 4. Management Commands (`tenants/management/commands/`)
- `create_tenant`: Create new tenant with database setup
- `list_tenants`: Display all tenants and their status
- `migrate_tenants`: Run migrations across all tenant databases

### 5. Utility Functions (`tenants/utils.py`)
- Tenant context switching
- Database connection management
- Validation and helper functions

## 🚀 Getting Started

### Step 1: Install and Setup

1. **Run Initial Migration**
   ```bash
   python manage.py makemigrations tenants
   python manage.py migrate
   ```

2. **Create Your First Tenant**
   ```bash
   python manage.py create_tenant "ABC Company" abc admin@abc.com --multi-location
   ```

### Step 2: Access Tenant

1. **Add subdomain to your hosts file** (for local development):
   ```
   127.0.0.1 abc.localhost
   ```

2. **Access tenant**: `http://abc.localhost:8000`

### Step 3: Create Additional Tenants
```bash
# Create more tenants
python manage.py create_tenant "XYZ Corp" xyz admin@xyz.com
python manage.py create_tenant "Demo Company" demo demo@example.com

# List all tenants
python manage.py list_tenants
```

## 📋 Management Commands

### Create Tenant
```bash
python manage.py create_tenant <name> <subdomain> <admin_email> [options]

Options:
--max-users <number>     Maximum users (default: 50)
--multi-location         Enable multi-location support
```

**Example:**
```bash
python manage.py create_tenant "Acme Corp" acme admin@acme.com --max-users 100 --multi-location
```

### List Tenants
```bash
python manage.py list_tenants [--active-only]
```

### Migrate Tenants
```bash
# Migrate all tenants
python manage.py migrate_tenants

# Migrate specific tenant
python manage.py migrate_tenants --tenant acme

# Migrate specific app for all tenants
python manage.py migrate_tenants --app sales_app
```

## 🔄 Development Workflow

### Adding New Features

1. **Create models/views as usual** - they'll automatically be tenant-aware
2. **Run migrations for all tenants**:
   ```bash
   python manage.py makemigrations
   python manage.py migrate_tenants
   ```

### Testing with Multiple Tenants

1. **Create test tenants**:
   ```bash
   python manage.py create_tenant "Test Org 1" test1 test1@example.com
   python manage.py create_tenant "Test Org 2" test2 test2@example.com
   ```

2. **Add to hosts file**:
   ```
   127.0.0.1 test1.localhost
   127.0.0.1 test2.localhost
   ```

3. **Test isolation**: Data created in one tenant should not appear in another

## 🏪 Multi-Location Support

For organizations with multiple locations:

1. **Enable during tenant creation**:
   ```bash
   python manage.py create_tenant "Multi Store Co" multistore admin@multistore.com --multi-location
   ```

2. **Add locations via admin interface** or programmatically:
   ```python
   from tenants.models import Tenant, TenantLocation
   
   tenant = Tenant.objects.get(subdomain='multistore')
   TenantLocation.objects.create(
       tenant=tenant,
       name='Downtown Store',
       code='DT',
       address='123 Main St'
   )
   ```

3. **Track performance per location** in your sales/accounting models

## 🔒 Security Considerations

### Data Isolation
- ✅ Complete database separation per tenant
- ✅ No cross-tenant data access possible
- ✅ Middleware enforces tenant context

### Access Control
- ✅ Users exist per tenant (no cross-tenant access)
- ✅ Admin interface separated from tenant data
- ✅ Subdomain validation prevents unauthorized access

## 🚀 Production Deployment

### Database Setup
Each tenant needs its own database. Configure your database server to support multiple databases:

```python
# Example production database configuration
TENANT_DATABASE_TEMPLATE = {
    'ENGINE': 'django.db.backends.postgresql',
    'USER': 'your_db_user',
    'PASSWORD': 'your_db_password',
    'HOST': 'your_db_host',
    'PORT': '5432',
    'OPTIONS': {
        'charset': 'utf8mb4',
    }
}
```

### DNS/Subdomain Setup
Configure your DNS to point all subdomains to your application:
```
*.yourapp.com → Your application server
```

### SSL Certificates
Use a wildcard SSL certificate for all subdomains:
```
*.yourapp.com
```

## 🧪 Testing Multi-Tenancy

### Unit Tests
```python
from django.test import TestCase
from tenants.utils import switch_tenant_context
from tenants.models import Tenant

class MultiTenantTest(TestCase):
    def test_tenant_isolation(self):
        tenant1 = Tenant.objects.create(name="Tenant 1", subdomain="t1")
        tenant2 = Tenant.objects.create(name="Tenant 2", subdomain="t2")
        
        # Test that data is isolated between tenants
        with switch_tenant_context(tenant1):
            # Create data for tenant1
            pass
            
        with switch_tenant_context(tenant2):
            # Verify tenant2 doesn't see tenant1's data
            pass
```

### Integration Tests
Test the full subdomain → tenant → database flow:

```python
from django.test import Client

def test_subdomain_routing():
    client = Client()
    response = client.get('/', HTTP_HOST='tenant1.testserver')
    # Assert correct tenant context
```

## 📊 Monitoring and Maintenance

### Health Checks
Monitor tenant database connections and performance:

```bash
# Check all tenant databases are accessible
python manage.py migrate_tenants --check
```

### Backup Strategy
Each tenant database should be backed up independently:

```bash
# Example backup script
for tenant in $(python manage.py list_tenants --active-only); do
    pg_dump sales_$tenant > backup_$tenant_$(date +%Y%m%d).sql
done
```

## 🔧 Troubleshooting

### Common Issues

1. **Tenant not found**: Check subdomain spelling and tenant status
2. **Database connection errors**: Verify tenant database exists and is accessible
3. **Migration failures**: Run `migrate_tenants` to sync all tenant databases
4. **Cross-tenant data leakage**: Verify middleware is properly configured

### Debug Commands
```bash
# Check tenant configuration
python manage.py list_tenants

# Verify database routing
python manage.py shell
>>> from tenants.utils import get_current_tenant
>>> # Test tenant context

# Check database connections
python manage.py dbshell --database sales_tenant1
```

## 📈 Scaling Considerations

### Current Limits
- **10 organizations** (configurable)
- **50 users per tenant** (configurable)
- **Multiple locations per tenant** (supported)

### Future Enhancements
- Automated tenant provisioning API
- Tenant-specific feature flags
- Custom branding per tenant
- Tenant usage analytics
- Automated scaling policies

This multi-tenancy implementation provides a solid foundation for scaling your Sales Management application to serve multiple organizations while maintaining complete data isolation and security.

## 💾 Database Architecture Deep Dive

### How the Database System Works

The multi-tenancy implementation uses a **database-per-tenant** approach with dynamic database routing:

#### 1. **Database Structure**
```
Default Database (sales_management)
├── tenants_tenant           # Tenant metadata
├── tenants_tenantlocation   # Location data  
├── auth_user               # Super admin users
├── django_migrations       # System migrations
└── admin tables           # Django admin data

Tenant Database 1 (sales_org1)
├── sales_app_*             # Organization 1's sales data
├── accounting_app_*        # Organization 1's accounting data
├── auth_user              # Organization 1's users
└── django_migrations      # Tenant-specific migrations

Tenant Database 2 (sales_org2)  
├── sales_app_*             # Organization 2's sales data
├── accounting_app_*        # Organization 2's accounting data
├── auth_user              # Organization 2's users
└── django_migrations      # Tenant-specific migrations
```

#### 2. **Database Router Logic**
The `TenantDatabaseRouter` automatically routes queries:

```python
# Shared Apps (always use 'default' database):
- tenants app (tenant metadata)
- admin interface
- authentication framework
- Django system tables

# Tenant Apps (use tenant-specific database):
- sales_app (invoices, customers, products)
- accounting_app (expenses, reports, taxes)
- custom business logic apps
```

#### 3. **Dynamic Database Connection**
When a request comes in:
1. `TenantMiddleware` extracts subdomain → identifies tenant
2. `TenantDatabaseRouter` routes queries to correct database
3. Django manages separate database connections per tenant

### 🔧 Database Configuration Options

#### **Option 1: Same Server, Multiple Databases (Current Default)**

**Best for:** Small to medium deployments (1-20 tenants)

```python
# settings.py - Current configuration
TENANT_DATABASE_TEMPLATE = {
    'ENGINE': 'django.db.backends.postgresql',
    'HOST': 'localhost',
    'PORT': '5432',
    'USER': 'sales_user',
    'PASSWORD': 'your_password',
    'OPTIONS': {'charset': 'utf8mb4'},
}

# Auto-generates:
# Database: sales_org1, sales_org2, sales_org3, etc.
# All on same PostgreSQL server
```

#### **Option 2: Specific Database URLs Per Tenant**

**Best for:** Large deployments, different database servers per tenant

Create a custom tenant model with database URL field:

```python
# tenants/models.py - Enhanced version
class Tenant(models.Model):
    name = models.CharField(max_length=100, unique=True)
    subdomain = models.CharField(max_length=63, unique=True)
    database_name = models.CharField(max_length=63, unique=True)
    
    # Add these fields for custom database URLs
    database_url = models.URLField(blank=True, help_text="Custom database URL")
    database_host = models.CharField(max_length=255, blank=True)
    database_port = models.PositiveIntegerField(null=True, blank=True)
    database_user = models.CharField(max_length=100, blank=True)
    database_password = models.CharField(max_length=100, blank=True)
    
    # ... rest of fields
    
    def get_database_config(self):
        """Return database configuration for this tenant"""
        if self.database_url:
            # Use custom URL
            import dj_database_url
            return dj_database_url.parse(self.database_url)
        else:
            # Use template with custom parameters
            config = settings.TENANT_DATABASE_TEMPLATE.copy()
            config['NAME'] = self.database_name
            
            if self.database_host:
                config['HOST'] = self.database_host
            if self.database_port:
                config['PORT'] = self.database_port
            if self.database_user:
                config['USER'] = self.database_user
            if self.database_password:
                config['PASSWORD'] = self.database_password
                
            return config
```

#### **Option 3: Different Database Types Per Tenant**

**Best for:** Mixed requirements (some tenants need PostgreSQL, others MySQL)

```python
# tenants/models.py
class Tenant(models.Model):
    # ... existing fields
    
    DATABASE_ENGINE_CHOICES = [
        ('postgresql', 'PostgreSQL'),
        ('mysql', 'MySQL'),
        ('sqlite3', 'SQLite'),
    ]
    
    database_engine = models.CharField(
        max_length=20,
        choices=DATABASE_ENGINE_CHOICES,
        default='postgresql'
    )
    
    def get_database_config(self):
        """Return database configuration with engine selection"""
        if self.database_engine == 'postgresql':
            config = {
                'ENGINE': 'django.db.backends.postgresql',
                'NAME': self.database_name,
                'HOST': self.database_host or 'localhost',
                'PORT': self.database_port or 5432,
                'USER': self.database_user,
                'PASSWORD': self.database_password,
            }
        elif self.database_engine == 'mysql':
            config = {
                'ENGINE': 'django.db.backends.mysql',
                'NAME': self.database_name,
                'HOST': self.database_host or 'localhost',
                'PORT': self.database_port or 3306,
                'USER': self.database_user,
                'PASSWORD': self.database_password,
            }
        elif self.database_engine == 'sqlite3':
            config = {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': f'{settings.BASE_DIR}/{self.database_name}.sqlite3',
            }
        
        return config
```

### 🚀 Setting Up Specific Database URLs

#### **Method 1: Environment Variables (Recommended)**

**For production with external databases:**

```bash
# .env file
DEFAULT_DATABASE_URL=postgresql://user:pass@main-db.com:5432/main_db

# Tenant-specific database URLs
TENANT_ORG1_DATABASE_URL=postgresql://org1:pass@tenant1-db.com:5432/org1_db
TENANT_ORG2_DATABASE_URL=postgresql://org2:pass@tenant2-db.com:5432/org2_db
TENANT_DEMO_DATABASE_URL=postgresql://demo:pass@demo-db.com:5432/demo_db
```

**Updated settings.py:**
```python
# settings.py
import os

# Function to get tenant database URL
def get_tenant_database_url(subdomain):
    """Get database URL for specific tenant"""
    env_var = f'TENANT_{subdomain.upper()}_DATABASE_URL'
    return os.getenv(env_var)

# Modified TENANT_DATABASE_TEMPLATE to support custom URLs
TENANT_DATABASE_TEMPLATE = {
    'ENGINE': 'django.db.backends.postgresql',
    'OPTIONS': {'charset': 'utf8mb4'},
}
```

#### **Method 2: Enhanced Create Tenant Command**

Update the create_tenant command to accept database parameters:

```bash
# Create tenant with custom database
python manage.py create_tenant "Big Client" bigclient admin@bigclient.com \
    --database-url "postgresql://bigclient:secure@bigclient-db.com:5432/bigclient_production"

# Create tenant with separate parameters
python manage.py create_tenant "Another Client" another admin@another.com \
    --database-host "another-db.com" \
    --database-port 5432 \
    --database-user "another_user" \
    --database-password "secure_password" \
    --database-name "another_production"
```

#### **Method 3: Admin Interface Configuration**

Add database configuration to Django admin:

```python
# tenants/admin.py
from django.contrib import admin
from .models import Tenant, TenantLocation

@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):
    list_display = ['name', 'subdomain', 'database_name', 'is_active', 'database_status']
    list_filter = ['is_active', 'supports_multi_location']
    search_fields = ['name', 'subdomain', 'admin_email']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'subdomain', 'admin_email', 'is_active')
        }),
        ('Database Configuration', {
            'fields': ('database_name', 'database_url', 'database_host', 
                      'database_port', 'database_user', 'database_password'),
            'classes': ('collapse',)
        }),
        ('Settings', {
            'fields': ('max_users', 'supports_multi_location')
        })
    )
    
    def database_status(self, obj):
        """Show database connection status"""
        try:
            from django.db import connections
            connections[obj.database_name].ensure_connection()
            return "✅ Connected"
        except:
            return "❌ Connection Failed"
    database_status.short_description = "DB Status"
```

### 🏭 Production Database Setup Examples

#### **AWS RDS Multi-Tenant Setup**
```bash
# Main database (tenant metadata)
export DEFAULT_DATABASE_URL="postgresql://admin:pass@main-rds.amazonaws.com:5432/main_db"

# Tenant databases on separate RDS instances
export TENANT_ENTERPRISE_DATABASE_URL="postgresql://enterprise:pass@enterprise-rds.amazonaws.com:5432/enterprise_db"
export TENANT_STARTUP_DATABASE_URL="postgresql://startup:pass@startup-rds.amazonaws.com:5432/startup_db"
```

#### **Google Cloud SQL Setup**
```bash
# Using Cloud SQL instances per major tenant
export TENANT_BIGCORP_DATABASE_URL="postgresql://bigcorp:pass@bigcorp-sql.googleapis.com:5432/bigcorp_production"
export TENANT_MEDIUMCO_DATABASE_URL="postgresql://mediumco:pass@shared-sql.googleapis.com:5432/mediumco_db"
```

#### **Hybrid Setup (Mix of shared and dedicated)**
```bash
# Small tenants share a database server
export TENANT_SMALL1_DATABASE_URL="postgresql://shared:pass@shared-db.com:5432/small1_db"
export TENANT_SMALL2_DATABASE_URL="postgresql://shared:pass@shared-db.com:5432/small2_db"

# Large tenants get dedicated servers
export TENANT_ENTERPRISE_DATABASE_URL="postgresql://enterprise:pass@enterprise-dedicated.com:5432/enterprise_db"
```

### 🔍 Database Management Commands

#### **Enhanced Management Commands**

```bash
# Test all tenant database connections
python manage.py test_tenant_connections

# Migrate specific tenant to new database
python manage.py migrate_tenant_database bigclient \
    --new-url "postgresql://bigclient:newpass@new-server.com:5432/bigclient_v2"

# Backup tenant database
python manage.py backup_tenant_database demo --output /backups/

# Restore tenant database
python manage.py restore_tenant_database demo --backup /backups/demo_backup.sql
```

This flexible database configuration allows you to:
- **Start simple** with all tenants on one database server
- **Scale up** by moving large tenants to dedicated servers
- **Mix configurations** based on tenant requirements and SLA needs
- **Support different database engines** per tenant if needed
