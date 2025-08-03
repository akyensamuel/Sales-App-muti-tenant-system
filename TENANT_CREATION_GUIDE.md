# Tenant Creation Guide - Sales Management System

## Overview
This guide covers creating and managing tenants in the multi-tenant sales management system. Each tenant gets their own isolated database and configuration.

---

## 🚀 Quick Start

### Basic Tenant Creation
```bash
python manage.py create_tenant "Company Name" "subdomain" "admin@email.com"
```

**Example:**
```bash
python manage.py create_tenant "ABC Corporation" "abc" "admin@abc.com"
```

This creates a tenant with:
- Default PostgreSQL database (auto-configured)
- 50 user limit
- Single location support
- Default superuser: Akyen / 08000000

---

## 📋 Command Options

| Option | Description | Default |
|--------|-------------|---------|
| `--max-users=N` | Maximum users allowed | 50 |
| `--multi-location` | Enable multi-location support | False |
| `--database-url="URL"` | Complete database URL | Auto-generated |
| `--database-engine` | Database engine | postgresql |
| `--database-host` | Database host | Auto-configured |
| `--database-port` | Database port | 5432 |
| `--database-user` | Database username | Auto-configured |
| `--database-password` | Database password | Auto-configured |

---

## 🎯 Production Examples

### 1. External PostgreSQL Database
```bash
python manage.py create_tenant "Tech Corp" "techcorp" "admin@techcorp.com" \
  --database-url="postgresql://user:pass@db.render.com:5432/techcorp_db" \
  --max-users=100 \
  --multi-location
```

### 2. Individual Database Parameters
```bash
python manage.py create_tenant "Retail Plus" "retail" "admin@retail.com" \
  --database-host="postgres.company.com" \
  --database-port=5432 \
  --database-user="retail_user" \
  --database-password="secure_password" \
  --max-users=200
```

### 3. Local Development
```bash
python manage.py create_tenant "Test Company" "test" "test@example.com"
```

## 🛠️ Management Commands

### View All Tenants
```bash
python manage.py setup_main_database
```

### Reset Tenant Database (Force Migration)
```bash
python manage.py force_migrate_tenant "subdomain"
```

### Manual Tenant Setup (Fallback)
```bash
python manage.py manual_setup_tenant "subdomain"
```

### Run Regular Migration
```bash
python manage.py migrate_tenant "subdomain"
```

---

## 🔍 What Happens During Creation

### ✅ Automatic Setup Process
1. **Tenant Record**: Creates tenant entry in main database
2. **Database Setup**: Configures tenant database connection
3. **Migrations**: Runs all Django migrations on tenant database
4. **Tables Created**: 
   - User management (auth_user, auth_group, etc.)
   - Sales app tables (customers, products, sales, etc.)
   - Accounting app tables (accounts, transactions, etc.)
   - Tenant-specific configuration tables

5. **Default Data**:
   - **Superuser**: Username: `Akyen`, Password: `08000000`
   - **Groups**: Admin, Managers, Cashiers
   - **Permissions**: Properly assigned to groups

6. **Access URLs Generated**:
   - Main: `http://subdomain.localhost:8000/`
   - Sales: `http://subdomain.localhost:8000/sales/`
   - Accounting: `http://subdomain.localhost:8000/accounting/`

---

## 🚨 Troubleshooting

### Common Issues

#### 1. Database Connection Errors
**Problem**: `could not connect to server`
```bash
# Check database URL format
python manage.py create_tenant "Test" "test" "test@test.com" \
  --database-url="postgresql://user:pass@correct-host:5432/dbname"
```

#### 2. Migration State Issues
**Problem**: Migrations show as applied but tables don't exist
```bash
# Use force migration to reset
python manage.py force_migrate_tenant "subdomain"
```

#### 3. Permission Errors
**Problem**: Database permission denied
```bash
# Ensure database user has CREATE DATABASE permission
# Or use manual setup as fallback
python manage.py manual_setup_tenant "subdomain"
```

#### 4. Subdomain Already Exists
**Problem**: `Subdomain 'test' already exists`
```bash
# Check existing tenants first
python manage.py setup_main_database
```

---

## 🔐 Security Checklist

### Production Deployment
- [ ] Change default superuser password immediately
- [ ] Update admin email to real email address
- [ ] Use environment variables for database credentials
- [ ] Configure proper domain names (not localhost)
- [ ] Set up SSL certificates
- [ ] Configure database backups
- [ ] Review user permissions and groups
- [ ] Set up monitoring and logging

### Database Security
- [ ] Use dedicated database users per tenant
- [ ] Apply principle of least privilege
- [ ] Enable database connection encryption
- [ ] Regular backup and recovery testing
- [ ] Monitor database access logs

---

## 📈 Scaling Considerations

### Performance Tips
1. **Database Hosting**: Use dedicated database servers for production
2. **Connection Pooling**: Configure appropriate connection limits
3. **Monitoring**: Set up database performance monitoring
4. **Backup Strategy**: Implement automated backups per tenant
5. **Resource Limits**: Monitor disk space and memory usage

### Multi-Tenant Architecture
- Each tenant has completely isolated data
- Tenant databases can be on different servers
- Main database only stores tenant configuration
- Supports horizontal scaling by tenant

---
2. **Migrations Run**: All tables created automatically
3. **Default Data**: Groups and superuser created
4. **Ready to Use**: Immediately accessible

### 🌐 **Production Mode (Remote Database)**
1. **Configuration Saved**: Database URL stored in main database
2. **Setup Deferred**: Migration skipped (database may not be accessible from dev machine)
3. **Instructions Provided**: Shows production setup steps
4. **Manual Steps Required**: Run migrations in production environment

### 📦 **Always Created**
- **Tenant Record**: Stored in main database
- **Database Configuration**: URL/connection details saved
- **Access URLs**: Subdomain routing configured
- **Default Credentials**: Superuser info provided

---

## 🔧 **Production Deployment Steps**

### **1. Create Tenant (Development)**
```bash
python manage.py create_tenant "Your Company" "yourco" "admin@yourco.com" \
  --database-url="postgresql://yourco_user:secure_pass@prod.db.com:5432/yourco_db"
```

### **2. Deploy to Production**
```bash
# Copy your code to production server
# Ensure database server is accessible
# Install required packages: psycopg2 or mysqlclient
```

### **3. Run Migrations (Production)**
```bash
python manage.py migrate --database=sales_yourco
```

### **4. Create Admin Users (Production)**
```bash
python manage.py create_tenant_admins
```

### **5. Update Settings (Production)**
```bash
# Update ALLOWED_HOSTS in settings.py
ALLOWED_HOSTS = ['yourco.yourdomain.com', '.yourdomain.com']
```

---

## 🚨 **Security Notes**

### **Database URLs with Credentials**
```bash
# ⚠️ WARNING: Database URLs contain sensitive information
--database-url="postgresql://user:PASSWORD@host:port/db"

# 🔒 SECURE: Use environment variables in production
--database-url="${DATABASE_URL}"
```

### **Default Credentials**
```
Username: Akyen
Password: 08000000
Email: lordsades1@gmail.com

🚨 CHANGE THESE IMMEDIATELY IN PRODUCTION!
```

---

## 📊 **Verification Commands**

### **List All Tenants**
```bash
python manage.py setup_main_database
```

### **Check Tenant Database**
```bash
python manage.py show_tenant_tables
```

### **Clean Main Database**
```bash
python manage.py clean_main_database --force
```

---

## 🌍 **Access Patterns**

### **Development URLs**
- Main App: `http://yourco.localhost:8000/`
- Accounting: `http://yourco.localhost:8000/accounting/`
- Sales: `http://yourco.localhost:8000/sales/`
- Admin: `http://yourco.localhost:8000/admin/`

### **Production URLs**
- Main App: `http://yourco.yourdomain.com/`
- Accounting: `http://yourco.yourdomain.com/accounting/`
- Sales: `http://yourco.yourdomain.com/sales/`
- Admin: `http://yourco.yourdomain.com/admin/`

---

## 🔄 **Database Architecture**

### **Main Database (`db.sqlite3`)**
```
✅ Tenant configurations
✅ Database URLs for routing
✅ Default groups (Admin, Managers, Cashiers)
❌ NO user accounts
```

### **Tenant Databases**
```
✅ Complete application data
✅ User accounts and authentication
✅ Sales and accounting records
✅ Isolated per organization
```

---

## 🆘 **Troubleshooting**

### **"Subdomain already exists"**
```bash
# Choose a different subdomain or delete existing tenant
python manage.py shell
>>> from tenants.models import Tenant
>>> Tenant.objects.filter(subdomain="yourco").delete()
```

### **"Could not connect to database"**
```bash
# This is expected in development for remote databases
# Database configuration is saved, run migrations in production
```

### **"MySQLdb module not found"**
```bash
# Install MySQL client in production
pip install mysqlclient
```

### **"psycopg2 not found"**
```bash
# Install PostgreSQL client in production
pip install psycopg2-binary
```

---

## 🎯 **Best Practices**

1. **Use Database URLs** for production environments
2. **Test locally** with SQLite first
3. **Change default passwords** immediately
4. **Use environment variables** for sensitive data
5. **Backup tenant databases** separately
6. **Monitor tenant resource usage**
7. **Use SSL/HTTPS** in production
8. **Configure proper domain names** (not .localhost)

---

This comprehensive command reference ensures you can create tenants for any environment with proper database configurations! 🚀
