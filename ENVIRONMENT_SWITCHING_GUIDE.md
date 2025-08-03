# 🔄 Environment Switching Guide

This guide shows you how to quickly switch between local development and production environments.

## 📁 Configuration Files

- **`.env`** - Your actual environment configuration (never commit this)
- **`.env.example`** - Template file (safe to commit)

## 🔄 Quick Environment Switch

### 💻 **Switch to LOCAL DEVELOPMENT** (SQLite)

**1. Edit `.env` file:**
```bash
# Comment out Supabase (add # at start)
# DATABASE_URL=postgresql://postgres.alxzgxrxefhfrcnfqryo:JL%25DF0WSu9TiNKC@aws-0-us-east-2.pooler.supabase.com:6543/postgres

# Uncomment SQLite (remove # at start)  
DATABASE_URL=sqlite:///db.sqlite3
```

**2. Run migrations:**
```bash
D:/code/Sales_App/virtual/Scripts/python.exe manage.py migrate
```

**3. Create local tenant:**
```bash
D:/code/Sales_App/virtual/Scripts/python.exe manage.py create_tenant "Local Dev" "local" "admin@local.com"
```

---

### 🌐 **Switch to PRODUCTION/ONLINE** (Supabase)

**1. Edit `.env` file:**
```bash
# Uncomment Supabase (remove # at start)
DATABASE_URL=postgresql://postgres.alxzgxrxefhfrcnfqryo:JL%25DF0WSu9TiNKC@aws-0-us-east-2.pooler.supabase.com:6543/postgres

# Comment out SQLite (add # at start)
# DATABASE_URL=sqlite:///db.sqlite3
```

**2. Run migrations:**
```bash
D:/code/Sales_App/virtual/Scripts/python.exe manage.py migrate
```

**3. Create production tenant:**
```bash
D:/code/Sales_App/virtual/Scripts/python.exe manage.py create_tenant "Production Test" "prodtest" "admin@prodtest.com" --database-url="postgresql://second_test_db_user:tEhjKsNWv0O3xj58NLPQNB22WCcMO6UF@dpg-d27r0n15pdvs73ftrfsg-a.oregon-postgres.render.com/second_test_db" --max-users=100 --multi-location
```

## 🎯 **Current Configuration**

Check your current configuration with:
```bash
D:/code/Sales_App/virtual/Scripts/python.exe manage.py check --deploy
```

## 🗂️ **Database Files**

### Local Development:
- **Main DB**: `db.sqlite3` (in project root)
- **Tenant DBs**: `tenant_dbs/tenant_name.sqlite3`

### Production:
- **Main DB**: Supabase PostgreSQL
- **Tenant DBs**: External PostgreSQL (Render, Heroku, etc.)

## 📝 **Tips**

1. **Quick Switch**: Use comment/uncomment in `.env` for fast switching
2. **Backup**: Always backup your local SQLite files before switching
3. **Migrations**: Run migrations after each switch to sync database schema
4. **Logs**: Check `logs/tenant_operations.log` for operation history
5. **Testing**: Use local SQLite for quick feature testing
6. **Production**: Use Supabase/PostgreSQL for realistic data testing

## ⚠️ **Important Notes**

- **Never commit `.env`** - it contains sensitive database credentials
- **Always migrate** after switching database configurations
- **Use local SQLite** for quick development and testing
- **Use production DBs** when testing integrations or deployment features
- **Check logs** in `logs/tenant_operations.log` to track all operations
