# Complete Multi-Tenant System Guide - Sales Management

**System Status**: ✅ Production Ready  
**Last Updated**: August 3, 2025  
**Database Architecture**: Supabase (Main) + External PostgreSQL (Tenants)

---

## 🚀 **CRITICAL INFORMATION YOU MUST KNOW**

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
D:/code/Sales_App/virtual/Scripts/python.exe manage.py create_tenant "Dev Company" "dev" "dev@dev.com" --max-users=25
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
# Run migrations for tenant
D:/code/Sales_App/virtual/Scripts/python.exe manage.py migrate_tenant subdomain

# Force reset database (for problems)
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

## 🚨 **COMMON ISSUES & SOLUTIONS**

### **1. Database Connection Issues**
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
├── Create: create_tenant "Name" "sub" "email" --database-url="url"
├── Delete: delete_tenant subdomain  
├── Status: setup_main_database
├── Fix DB: force_migrate_tenant subdomain
└── Logs: type logs\tenant_operations.log

🔐 DEFAULT LOGIN: Akyen / 08000000 (CHANGE THIS!)
🌐 ACCESS: http://subdomain.localhost:8000/
📧 ADMIN: Update default email immediately
🔒 SECURITY: Review permissions and passwords
```

**Keep this guide accessible - it contains everything you need to manage your multi-tenant system!** 📚
