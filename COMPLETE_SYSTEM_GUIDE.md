# Complete Multi-Tenant System Guide - Sales Management

**System Status**: ✅ Production Ready  
**Last Updated**: August 3, 2025  
**Database Architecture**: Supabase (Main) + External PostgreSQL (Tenants)

---

## 🚀 **CRITICAL INFO### **6. Local Development - Wrong Commands**
```
❌ Problem: Using production commands for local development
✅ Solution:
   - For LOCAL: Use create_tenant WITHOUT --database-url
   - For PRODUCTION: Use create_tenant WITH --database-url
   - NEVER use migrate_tenant for new tenants

# LOCAL (SQLite) - Current Working Example:
D:/code/Sales_App/virtual/Scripts/python.exe manage.py create_tenant "Winkayd Company" "winkayd" "winsco@gmail.com" --database-engine="django.db.backends.sqlite3" --max-users=25

# PRODUCTION (PostgreSQL):
D:/code/Sales_App/virtual/Scripts/python.exe manage.py create_tenant "Prod Company" "prod" "admin@prod.com" --database-url="postgresql://..." --max-users=100
```

### **7. User Group Assignment Issues**
```
❌ Problem: User "Akyen" not assigned to all required groups (Admin, Managers, Cashiers)
✅ Solution:
   - Fixed in tenants/models.py to assign user to ALL groups
   - Delete and recreate tenant if created before the fix
   - Use check_tenant_user command to verify/fix groups

# Check user groups
D:/code/Sales_App/virtual/Scripts/python.exe manage.py check_tenant_user winkayd

# Fix by recreating tenant (if needed):
D:/code/Sales_App/virtual/Scripts/python.exe manage.py delete_tenant winkayd --force
D:/code/Sales_App/virtual/Scripts/python.exe manage.py create_tenant "Winkayd Company" "winkayd" "winsco@gmail.com" --database-engine="django.db.backends.sqlite3" --max-users=25
```

### **8. SQLite Foreign Key Constraint Errors**
```
❌ Problem: "FOREIGN KEY constraint failed" in admin panel
✅ Solution:
   - Ensure user is properly assigned to all groups
   - Use the fixed tenant creation process
   - Avoid editing users directly in admin panel initially

# Safe approach:
1. Create tenant with fixed code
2. Verify groups using check_tenant_user command  
3. Then use admin panel for additional users
```ST KNOW**

### **Environment Setup - ESSENTIAL**
```bash
# Your Python Environment Path (SAVE THIS!)
D:/code/Sales_App/virtual/Scripts/python.exe

# Your Working Directory
cd "d:\code\Sales_App\sales_management_project"

# Main Database Connection (Supabase)
DATABASE_URL=postgresql://postgres.alxzgxrxefhfrcnfqryo:JL%25DF0WSu9TiNKC@aws-0-us-east-2.pooler.supabase.com:6543/postgres
```

### **System Architecture - CRUCIAL**
```
🏢 Multi-Tenant Architecture:
├── 📊 Main Database (Supabase PostgreSQL)
│   ├── Tenant configurations ONLY
│   ├── Database URLs for routing
│   ├── Default groups (Admin/Managers/Cashiers)
│   └── NO user accounts (security feature)
│
└── 🗄️ Tenant Databases (External PostgreSQL)
    ├── Complete data isolation per tenant
    ├── All user accounts & authentication
    ├── Sales, inventory, accounting data
    └── Independent scaling per organization
```

---

## 🎯 **ONE-LINER COMMANDS - PRODUCTION READY**

### **Create New Tenant (MOST IMPORTANT)**
```bash
# Template Command
D:/code/Sales_App/virtual/Scripts/python.exe manage.py create_tenant "Company Name" "subdomain" "admin@email.com" --database-url="postgresql://user:password@host:port/database" --max-users=100 --multi-location

# Working Example (Final Production Company)
D:/code/Sales_App/virtual/Scripts/python.exe manage.py create_tenant "Final Production Company" "final" "admin@final.com" --database-url="postgresql://second_test_db_user:tEhjKsNWv0O3xj58NLPQNB22WCcMO6UF@dpg-d27r0n15pdvs73ftrfsg-a.oregon-postgres.render.com/second_test_db" --max-users=100 --multi-location

# Local Development (SQLite)
D:/code/Sales_App/virtual/Scripts/python.exe manage.py create_tenant "tenant Limited" "tenant" "tenant@email.com" --database-engine="django.db.backends.sqlite3" --max-users=25
```

### **Delete Tenant (WITH CONFIRMATION)**
```bash
# Safe deletion (requires typing confirmation)
D:/code/Sales_App/virtual/Scripts/python.exe manage.py delete_tenant subdomain

# Force deletion (skip confirmation)
D:/code/Sales_App/virtual/Scripts/python.exe manage.py delete_tenant subdomain --force

# Keep database (only remove from main DB)
D:/code/Sales_App/virtual/Scripts/python.exe manage.py delete_tenant subdomain --keep-database
```

### **Database Management**
```bash
# ⚠️ IMPORTANT: migrate_tenant is for EXISTING tenants with issues ONLY
# For new tenants, create_tenant does ALL the work automatically!

# Run migrations for EXISTING tenant (if needed)
D:/code/Sales_App/virtual/Scripts/python.exe manage.py migrate_tenant subdomain

# 🎯 FOR LOCAL DEVELOPMENT: Use create_tenant with SQLite engine
D:/code/Sales_App/virtual/Scripts/python.exe manage.py create_tenant "Company Name" "subdomain" "email@domain.com" --database-engine="django.db.backends.sqlite3" --max-users=25

# Force reset database (for serious problems)
D:/code/Sales_App/virtual/Scripts/python.exe manage.py force_migrate_tenant subdomain

# Manual setup (fallback method)
D:/code/Sales_App/virtual/Scripts/python.exe manage.py manual_setup_tenant subdomain

# Check system status
D:/code/Sales_App/virtual/Scripts/python.exe manage.py setup_main_database
```

---

## 🔐 **DEFAULT LOGIN CREDENTIALS - CHANGE IMMEDIATELY**

### **Every New Tenant Gets:**
```
🔑 Default Superuser:
   Username: Akyen
   Password: 08000000
   Email: lordsades1@gmail.com (update this!)
   Groups: Admin, Managers, Cashiers

⚠️  SECURITY WARNING:
   1. Change password IMMEDIATELY in production
   2. Update email to real admin email
   3. Create additional users as needed
   4. Review and adjust permissions
```

### **Access URLs for Each Tenant:**
```
🌐 URL Pattern: http://subdomain.localhost:8000/

Example for "final" tenant:
   Main App: http://final.localhost:8000/
   Sales: http://final.localhost:8000/sales/
   Accounting: http://final.localhost:8000/accounting/
```

---

## 📝 **COMPREHENSIVE LOGGING SYSTEM**

### **Log File Location:**
```
📂 logs/tenant_operations.log

Log Format:
2025-08-03 18:56:05 - INFO - TENANT_CREATE_SUCCESS | Subdomain: final | Name: Final Production Company | Database: sales_final | Access_URL: http://final.localhost:8000/ | Admin: admin@final.com | Database_URL: postgresql://user:****@host/db
```

### **What Gets Logged:**
- ✅ Tenant creation (start, success, errors)
- ✅ Tenant deletion (start, success, errors)
- ✅ Database URLs (with masked passwords)
- ✅ Access URLs and admin emails
- ✅ Timestamps for all operations

---

## � **LOCAL DEVELOPMENT WORKFLOW**

### **Creating Local Tenants (SQLite)**
```bash
# 1. Ensure you're in local development mode (.env file)
DATABASE_URL=sqlite:///db.sqlite3

# 2. Create local tenant (NO --database-url needed for SQLite)
D:/code/Sales_App/virtual/Scripts/python.exe manage.py create_tenant "test Company" "test" "test@gmail.com" --max-users=25

# 3. Verify tenant was created
D:/code/Sales_App/virtual/Scripts/python.exe manage.py setup_main_database

# 4. Access your tenant
# URL: http://test.localhost:8000/
# Login: Akyen / 08000000
```

### **Working with Existing Local Tenants**
```bash
# List all tenants
D:/code/Sales_App/virtual/Scripts/python.exe manage.py setup_main_database

# For existing tenants, DON'T use migrate_tenant - use create_tenant for new ones!
# If you need to fix an existing tenant:
D:/code/Sales_App/virtual/Scripts/python.exe manage.py force_migrate_tenant test

# Delete local tenant if needed
D:/code/Sales_App/virtual/Scripts/python.exe manage.py delete_tenant test
```

---

## �🚨 **COMMON ISSUES & SOLUTIONS**

### **1. "migrate_tenant" Command Confusion - UPDATED**
```
❌ Problem: Using "migrate_tenant" for new tenants or wrong database engine
✅ Solution: 
   - Use "create_tenant" for NEW tenants (does everything automatically)
   - Always specify --database-engine="django.db.backends.sqlite3" for local development
   - Use "migrate_tenant" ONLY for existing tenants with database issues

# ✅ CORRECT for local development (NEW tenant):
D:/code/Sales_App/virtual/Scripts/python.exe manage.py create_tenant "Fakstins Limited" "fakstins" "fakstins@yahoo.com" --database-engine="django.db.backends.sqlite3" --max-users=25

# ❌ WRONG: python manage.py migrate_tenant fakstins (for new tenant)
# ❌ WRONG: create_tenant without --database-engine (defaults to PostgreSQL)

# ✅ ONLY use migrate_tenant for existing tenant with issues:
D:/code/Sales_App/virtual/Scripts/python.exe manage.py migrate_tenant fakstins
```

### **2. Database Connection Issues**
```
❌ Problem: "could not connect to server"
✅ Solution: 
   - Check database URL format
   - Verify credentials are correct
   - Test connection manually
   - Use force_migrate_tenant command

# Test connection
D:/code/Sales_App/virtual/Scripts/python.exe manage.py check
```

### **2. Migration State Problems**
```
❌ Problem: "relation does not exist" or "table already exists"
✅ Solution:
   - Use force migration to reset
   - Try manual setup as fallback

# Commands
D:/code/Sales_App/virtual/Scripts/python.exe manage.py force_migrate_tenant subdomain
D:/code/Sales_App/virtual/Scripts/python.exe manage.py manual_setup_tenant subdomain
```

### **3. Subdomain Access Issues**
```
❌ Problem: "subdomain.localhost not resolving"
✅ Solution: Add to Windows hosts file

Location: C:\Windows\System32\drivers\etc\hosts
Add these lines:
127.0.0.1 final.localhost
127.0.0.1 test.localhost
127.0.0.1 dev.localhost
```

### **4. Permission Errors**
```
❌ Problem: "permission denied" database operations
✅ Solution:
   - Ensure database user has CREATE DATABASE permission
   - Check database connection string
   - Use manual setup with raw SQL

# Manual setup command
D:/code/Sales_App/virtual/Scripts/python.exe manage.py manual_setup_tenant subdomain
```

### **5. Tenant Already Exists**
```
❌ Problem: "Subdomain 'test' already exists"
✅ Solution:
   - Check existing tenants first
   - Delete old tenant if needed
   - Choose different subdomain

# Check existing tenants
D:/code/Sales_App/virtual/Scripts/python.exe manage.py setup_main_database

# Delete if needed
D:/code/Sales_App/virtual/Scripts/python.exe manage.py delete_tenant old_subdomain
```

### **6. Local Development - Wrong Commands**
```
❌ Problem: Using production commands for local development
✅ Solution:
   - For LOCAL: Use create_tenant WITHOUT --database-url
   - For PRODUCTION: Use create_tenant WITH --database-url
   - NEVER use migrate_tenant for new tenants

# LOCAL (SQLite) - Current Working Example:
D:/code/Sales_App/virtual/Scripts/python.exe manage.py create_tenant "test Company" "test" "winsco@gmail.com" --max-users=25

# PRODUCTION (PostgreSQL):
D:/code/Sales_App/virtual/Scripts/python.exe manage.py create_tenant "Prod Company" "prod" "admin@prod.com" --database-url="postgresql://..." --max-users=100
```

---

## 🛡️ **SECURITY BEST PRACTICES**

### **Production Deployment Checklist:**
```
🔐 CRITICAL SECURITY STEPS:
├── ✅ Change default superuser password
├── ✅ Update admin email to real email
├── ✅ Use environment variables for secrets
├── ✅ Configure proper domain names (not localhost)
├── ✅ Set up SSL certificates
├── ✅ Configure database backups
├── ✅ Review user permissions and groups
├── ✅ Monitor logs for suspicious activity
└── ✅ Regular security updates
```

### **Database Security:**
```
🗄️ DATABASE PROTECTION:
├── ✅ Use dedicated database users per tenant
├── ✅ Apply principle of least privilege
├── ✅ Enable database connection encryption
├── ✅ Regular backup and recovery testing
├── ✅ Monitor database access logs
└── ✅ Use strong passwords (not the default!)
```

---

## 📊 **MONITORING & MAINTENANCE**

### **Health Check Commands:**
```bash
# System health check
D:/code/Sales_App/virtual/Scripts/python.exe manage.py check

# View all tenants
D:/code/Sales_App/virtual/Scripts/python.exe manage.py setup_main_database

# Check specific tenant
D:/code/Sales_App/virtual/Scripts/python.exe manage.py migrate_tenant subdomain --dry-run

# View logs
type logs\tenant_operations.log
```

### **Regular Maintenance Tasks:**
```
📅 WEEKLY:
├── Review tenant operations log
├── Check database performance
├── Verify backups are working
└── Monitor disk space usage

📅 MONTHLY:
├── Update security patches
├── Review user accounts and permissions
├── Test disaster recovery procedures
└── Analyze system performance metrics
```

---

## 🔄 **BACKUP & DISASTER RECOVERY**

### **What to Backup:**
```
💾 CRITICAL BACKUPS:
├── 📊 Main Database (Supabase) - tenant configurations
├── 🗄️ Each Tenant Database - complete application data
├── 📝 Environment files (.env)
├── 📋 Management commands and custom code
└── 📂 logs/ directory for audit trail
```

### **Recovery Procedures:**
```bash
# Recreate tenant from backup
D:/code/Sales_App/virtual/Scripts/python.exe manage.py create_tenant "Restored Company" "restored" "admin@restored.com" --database-url="backup_database_url"

# Force setup if needed
D:/code/Sales_App/virtual/Scripts/python.exe manage.py force_migrate_tenant restored

# Manual setup as last resort
D:/code/Sales_App/virtual/Scripts/python.exe manage.py manual_setup_tenant restored
```

---

## 🚀 **SCALING CONSIDERATIONS**

### **Performance Optimization:**
```
⚡ SCALING STRATEGIES:
├── 🗄️ Use dedicated database servers per tenant
├── 🔗 Configure connection pooling
├── 📊 Monitor database performance metrics
├── 📈 Implement horizontal scaling by tenant
├── 🔄 Set up load balancing for high traffic
└── 📱 Consider database sharding for massive scale
```

### **Cost Optimization:**
```
💰 COST MANAGEMENT:
├── 🏢 Group small tenants on shared databases
├── 📊 Monitor resource usage per tenant
├── 🔄 Archive inactive tenant data
├── 📈 Scale resources based on actual usage
└── 🔍 Regular cost analysis and optimization
```

---

## 📞 **EMERGENCY CONTACT & SUPPORT**

### **Critical Files to Know:**
```
📂 IMPORTANT FILES:
├── 📄 .env - Database connection settings
├── 📋 tenants/models.py - Tenant configuration
├── 🔧 tenants/management/commands/ - All management commands
├── 📝 logs/tenant_operations.log - Operation history
├── 📚 This guide - Complete reference
└── 🔒 .gitignore - Security exclusions
```

### **Emergency Commands:**
```bash
# System completely broken? Reset everything:
D:/code/Sales_App/virtual/Scripts/python.exe manage.py check
D:/code/Sales_App/virtual/Scripts/python.exe manage.py setup_main_database

# Tenant broken? Force reset:
D:/code/Sales_App/virtual/Scripts/python.exe manage.py force_migrate_tenant subdomain

# Database corrupted? Manual recreation:
D:/code/Sales_App/virtual/Scripts/python.exe manage.py manual_setup_tenant subdomain

# Last resort? Delete and recreate:
D:/code/Sales_App/virtual/Scripts/python.exe manage.py delete_tenant subdomain --force
# Then recreate with original database URL
```

---

## 🎯 **QUICK REFERENCE CARD**

```
🚀 MOST USED COMMANDS:
├── Create Local: create_tenant "Name" "sub" "email" --database-engine="django.db.backends.sqlite3" --max-users=25
├── Create Production: create_tenant "Name" "sub" "email" --database-url="url" --max-users=100
├── Delete: delete_tenant subdomain  
├── Status: setup_main_database
├── Fix DB: force_migrate_tenant subdomain
└── Logs: type logs\tenant_operations.log

🔐 DEFAULT LOGIN: Akyen / 08000000 (CHANGE THIS!)
🌐 ACCESS: http://subdomain.localhost:8000/
📧 ADMIN: Update default email immediately
🔒 SECURITY: Review permissions and passwords

💻 LOCAL DEVELOPMENT (CRITICAL - SPECIFY DATABASE ENGINE):
├── Environment: DATABASE_URL=sqlite:///db.sqlite3
├── Create: create_tenant "Name" "sub" "email" --database-engine="django.db.backends.sqlite3" --max-users=25
├── Access: http://subdomain.localhost:8000/
├── Current Example: Winkayd tenant at http://winkayd.localhost:8000/
└── Current Example: Fakstins tenant at http://fakstins.localhost:8000/

🌐 PRODUCTION:
├── Environment: DATABASE_URL=postgresql://supabase-url
├── Create: create_tenant "Name" "sub" "email" --database-url="external-db"
├── Access: https://subdomain.yourdomain.com/
└── Current Example: Final tenant with Render PostgreSQL

⚠️ CRITICAL: Always use --database-engine="django.db.backends.sqlite3" for local development!
```

**Keep this guide handy - it contains everything you need to manage this multi-tenant system, and if there are any issues reach out to me** 📚