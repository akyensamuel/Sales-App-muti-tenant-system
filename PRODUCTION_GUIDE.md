# Production Deployment Guide - Sales Management System

## System Overview
This is a production-ready multi-tenant sales management system with complete data isolation, built on Django 5.2 with PostgreSQL and Supabase integration.

## Architecture Summary

### **Database Architecture**
- **Main Database**: Supabase PostgreSQL stores tenant configurations only
- **Tenant Databases**: Separate PostgreSQL databases per tenant (complete isolation)
- **No Shared User Data**: Users exist only in their respective tenant databases
- **Automatic Routing**: Custom middleware handles subdomain-to-database routing

### **Multi-Tenancy Features**
- **Complete Data Isolation**: Each tenant has separate database
- **Subdomain Access**: `tenant.yourdomain.com` routing
- **Scalable**: Supports unlimited tenants
- **Secure**: No cross-tenant data access possible

## Deployment Checklist

### ✅ 1. Environment Setup
- **Main Database**: Supabase PostgreSQL configured
- **Environment Variables**: `.env` with DATABASE_URL set
- **Security**: All sensitive files in `.gitignore`
- **Dependencies**: `requirements.txt` ready for deployment

### ✅ 2. Database Configuration
- **Main Database Migration**: Run on Supabase
- **Tenant Template**: Default groups (Admin, Managers, Cashiers) ready
- **Database Router**: Custom router handles multi-database operations
- **Connection Management**: Optimized for production workloads

### ✅ 3. Tenant Management System
- **Automated Creation**: Single command creates complete tenant setup
- **Default Superuser**: Akyen/08000000 (change in production)
- **Group Assignment**: Automatic role-based access control
- **Database Validation**: Connection testing and error handling

## Production Commands

### Create Production Tenant
```bash
python manage.py create_tenant "Company Name" "subdomain" "admin@company.com" \
  --database-url="postgresql://user:pass@host:port/dbname" \
  --max-users=100 \
  --multi-location
```

### Examples by Database Provider

#### Render PostgreSQL
```bash
python manage.py create_tenant "Tech Corp" "techcorp" "admin@techcorp.com" \
  --database-url="postgresql://user:pass@db.render.com:5432/techcorp_db"
```

#### AWS RDS
```bash
python manage.py create_tenant "Enterprise Co" "enterprise" "admin@enterprise.com" \
  --database-url="postgresql://user:pass@rds.amazonaws.com:5432/enterprise_db"
```

#### Google Cloud SQL
```bash
python manage.py create_tenant "Cloud Corp" "cloud" "admin@cloud.com" \
  --database-url="postgresql://user:pass@cloudsql.googleapis.com:5432/cloud_db"
```

#### Production with Individual Parameters:
```bash
python manage.py create_tenant "ABC Corporation" "abc" "admin@abc.com" \
  --database-engine="django.db.backends.postgresql" \
  --database-host="db.company.com" \
  --database-port=5432 \
  --database-user="abc_user" \
  --database-password="secure_password" \
  --max-users=100 \
  --multi-location
```

#### MySQL Example:
```bash
python manage.py create_tenant "XYZ Company" "xyz" "admin@xyz.com" \
  --database-url="mysql://user:password@mysql.company.com:3306/xyz_database"
```

This will:
- Create tenant database with specified URL/configuration
- Store database URL in main database for routing
- Run all migrations on the new database
- Create groups (Admin, Managers, Cashiers)
- Create superuser (Akyen/08000000/lordsades1@gmail.com)
- Make tenant accessible at `http://abc.localhost:8000/`

### Clean Main Database
```bash
python manage.py clean_main_database --force
```
Removes all users from main database, keeping only tenant configs and groups.

### Setup Main Database
```bash
python manage.py setup_main_database
```
Sets up main database with required groups and displays tenant information.

### Production Deployment
```bash
python manage.py deploy_production --create-sample-tenant
```
Prepares system for production with checklist and optional sample tenant.

## Database Architecture

### Main Database (`db.sqlite3`)
```
Tables:
- tenants_tenant (tenant configurations)
- tenants_tenantlocation (location tracking)
- auth_group (Admin, Managers, Cashiers templates)
- django_migrations, django_content_type (Django core)
- NO auth_user table entries
```

### Tenant Databases (`tenant_dbs/sales_{subdomain}.sqlite3`)
```
Tables:
- auth_user, auth_group, auth_permission (tenant users)
- sales_app_* (all sales application tables)
- accounting_app_* (all accounting application tables)
- django_migrations, django_content_type (Django core)
```

## Access Patterns

### ✅ Correct Access (Tenant Subdomains)
- `http://abc.localhost:8000/` → ABC Company homepage
- `http://abc.localhost:8000/accounting/` → ABC Company accounting
- `http://abc.localhost:8000/sales/` → ABC Company sales

### ❌ Blocked Access (Main Domain)
- `http://localhost:8000/accounting/` → Shows tenant selection page
- `http://localhost:8000/sales/` → Shows tenant selection page

### ✅ Allowed Main Domain Access
- `http://localhost:8000/` → Main homepage with tenant selection
- `http://localhost:8000/admin/` → Main database admin (tenant management)

## Production Deployment Checklist

### Environment Configuration
- [ ] Set `DEBUG=False`
- [ ] Generate new `SECRET_KEY`
- [ ] Configure `ALLOWED_HOSTS` with actual domain names
- [ ] Set up production database (PostgreSQL/MySQL)
- [ ] Configure email backend
- [ ] Set up HTTPS/SSL certificates

### Tenant Security
- [ ] Change default superuser passwords for all tenants
- [ ] Update admin emails to real addresses
- [ ] Configure proper domain names (not .localhost)
- [ ] Test tenant isolation
- [ ] Set up backup procedures for tenant databases

### Server Configuration
- [ ] Use production WSGI server (Gunicorn/uWSGI)
- [ ] Set up reverse proxy (Nginx/Apache)
- [ ] Configure static file serving
- [ ] Set up monitoring and logging
- [ ] Configure automated backups

## Migration Guide for Production

### 1. Database Migration
If using PostgreSQL/MySQL in production, update `TENANT_DATABASE_TEMPLATE` in settings:

```python
TENANT_DATABASE_TEMPLATE = {
    'ENGINE': 'django.db.backends.postgresql',
    'HOST': 'your-db-host',
    'PORT': '5432',
    'USER': 'your-db-user',
    'PASSWORD': 'your-db-password',
    'OPTIONS': {
        'charset': 'utf8mb4',
    },
}
```

### 2. Domain Configuration
Update `ALLOWED_HOSTS` in settings for production domains:

```python
ALLOWED_HOSTS = [
    'yourdomain.com',
    '.yourdomain.com',  # Allow all subdomains
    'www.yourdomain.com',
]
```

### 3. SSL Configuration
Configure HTTPS settings:

```python
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
```

## Troubleshooting

### Issue: "no such table: main.auth_user"
**Solution**: This was the original issue - fixed by ensuring auth tables exist in tenant databases.

### Issue: Tenant not accessible
**Check**: 
1. Tenant exists in main database
2. Tenant database file exists in `tenant_dbs/`
3. Subdomain is correctly configured
4. Accessing via proper subdomain URL

### Issue: Admin can't login
**Solution**: Use the default credentials:
- Username: `Akyen`
- Password: `08000000`
- Or create new admin user in tenant database

### Issue: Migrations not working
**Check**:
1. Database router is properly configured
2. Tenant database is loaded in Django settings
3. Apps are listed in migration configuration

## Security Notes

⚠️ **IMPORTANT**: Change these defaults in production:
- Default superuser password (`08000000`)
- Default superuser email (`lordsades1@gmail.com`)
- SECRET_KEY in Django settings
- Database passwords and credentials

## Support and Maintenance

### Backup Strategy
- Main database contains tenant configurations
- Each tenant database should be backed up separately
- Include both database files and media files

### Monitoring
- Monitor main database for tenant configurations
- Monitor individual tenant databases for application data
- Set up alerts for database connectivity issues
- Track tenant resource usage

### Scaling
- Consider database sharding for large numbers of tenants
- Implement connection pooling for high traffic
- Use read replicas for better performance
- Consider separate application servers per tenant group
