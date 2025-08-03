# Database Configuration Examples for Multi-Tenant Sales Management System

## Overview
This file contains practical examples for configuring different database setups
for your multi-tenant Sales Management System.

## 🏗️ Architecture Options

### Option 1: Single Server, Multiple Databases (Recommended for < 20 tenants)
All tenants share the same PostgreSQL server but have separate databases.

```bash
# .env configuration
DATABASE_URL=postgresql://admin:password@localhost:5432/sales_main

# Create tenants using default template
python manage.py create_tenant "Company A" companya admin@companya.com
python manage.py create_tenant "Company B" companyb admin@companyb.com
```

**Results in:**
- Main database: `sales_main` (tenant metadata)
- Tenant databases: `sales_companya`, `sales_companyb`
- All on same server: `localhost:5432`

### Option 2: Dedicated Database Servers per Tenant
Large tenants get their own database servers for performance/isolation.

```bash
# Create tenant with dedicated server
python manage.py create_tenant_advanced "Enterprise Corp" enterprise admin@enterprise.com \
    --database-url "postgresql://enterprise:securepass@enterprise-db.com:5432/enterprise_production" \
    --max-users 500

# Create tenant with shared server but custom credentials
python manage.py create_tenant_advanced "Startup Co" startup admin@startup.com \
    --database-host "shared-db.com" \
    --database-user "startup_user" \
    --database-password "startup_pass" \
    --database-name "startup_db"
```

### Option 3: Mixed Database Types
Different tenants can use different database engines.

```bash
# PostgreSQL tenant (recommended for production)
python manage.py create_tenant_advanced "PG Company" pgco admin@pgco.com \
    --database-engine postgresql \
    --database-host "pg-server.com"

# MySQL tenant (for specific requirements)
python manage.py create_tenant_advanced "MySQL Company" mysqlco admin@mysqlco.com \
    --database-engine mysql \
    --database-host "mysql-server.com" \
    --database-port 3306

# SQLite tenant (for development/demo)
python manage.py create_tenant_advanced "Demo Company" demo admin@demo.com \
    --database-engine sqlite3
```

## 🌐 Production Environment Examples

### AWS RDS Setup

#### Multi-AZ PostgreSQL with Read Replicas
```bash
# Production environment variables
export DATABASE_URL="postgresql://admin:secure@main-rds.amazonaws.com:5432/sales_main"

# Large enterprise tenant with dedicated RDS instance
python manage.py create_tenant_advanced "BigCorp International" bigcorp admin@bigcorp.com \
    --database-url "postgresql://bigcorp:ultra_secure@bigcorp-rds.amazonaws.com:5432/bigcorp_production" \
    --max-users 1000 \
    --multi-location

# Medium tenant on shared RDS with separate database
python manage.py create_tenant_advanced "MediumCo" mediumco admin@mediumco.com \
    --database-host "shared-rds.amazonaws.com" \
    --database-user "mediumco_user" \
    --database-password "medium_secure_pass" \
    --database-name "mediumco_prod"
```

#### Aurora Serverless for Variable Workloads
```bash
# Tenant using Aurora Serverless (auto-scaling)
python manage.py create_tenant_advanced "FlexCorp" flexcorp admin@flexcorp.com \
    --database-url "postgresql://flexcorp:flex_pass@aurora-serverless.cluster-xyz.us-east-1.rds.amazonaws.com:5432/flexcorp_db"
```

### Google Cloud SQL Setup

```bash
# Main database on Cloud SQL
export DATABASE_URL="postgresql://postgres:secure@/sales_main?host=/cloudsql/project:region:instance"

# Tenant with dedicated Cloud SQL instance
python manage.py create_tenant_advanced "GoogleCorp" googlecorp admin@googlecorp.com \
    --database-url "postgresql://googlecorp:secure@/googlecorp_db?host=/cloudsql/project:region:googlecorp-instance"

# Tenant on shared Cloud SQL with separate database
python manage.py create_tenant_advanced "SharedCorp" sharedcorp admin@sharedcorp.com \
    --database-host "/cloudsql/project:region:shared-instance" \
    --database-user "sharedcorp" \
    --database-password "shared_secure" \
    --database-name "sharedcorp_db"
```

### Azure Database for PostgreSQL

```bash
# Main database on Azure
export DATABASE_URL="postgresql://admin@azure-main:secure@azure-main.postgres.database.azure.com:5432/sales_main"

# Enterprise tenant with dedicated Azure instance
python manage.py create_tenant_advanced "AzureCorp" azurecorp admin@azurecorp.com \
    --database-url "postgresql://azurecorp@azure-tenant:secure@azurecorp.postgres.database.azure.com:5432/azurecorp_prod"
```

## 🔧 Development Environment Setup

### Local PostgreSQL with Multiple Databases

```bash
# Start PostgreSQL locally
createdb sales_main
createdb sales_demo
createdb sales_test1
createdb sales_test2

# Set environment
export DATABASE_URL="postgresql://localhost:5432/sales_main"

# Create test tenants
python manage.py create_tenant "Demo Company" demo admin@demo.com
python manage.py create_tenant "Test Company 1" test1 admin@test1.com
python manage.py create_tenant "Test Company 2" test2 admin@test2.com

# Update hosts file for local development
echo "127.0.0.1 demo.localhost" >> /etc/hosts
echo "127.0.0.1 test1.localhost" >> /etc/hosts
echo "127.0.0.1 test2.localhost" >> /etc/hosts
```

### Docker Compose Setup

```yaml
# docker-compose.yml
version: '3.8'
services:
  main-db:
    image: postgres:13
    environment:
      POSTGRES_DB: sales_main
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    ports:
      - "5432:5432"
    volumes:
      - main_db_data:/var/lib/postgresql/data

  tenant-db:
    image: postgres:13
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    ports:
      - "5433:5432"
    volumes:
      - tenant_db_data:/var/lib/postgresql/data

volumes:
  main_db_data:
  tenant_db_data:
```

```bash
# Start databases
docker-compose up -d

# Configure environment
export DATABASE_URL="postgresql://postgres:postgres@localhost:5432/sales_main"

# Create tenant using separate Docker PostgreSQL
python manage.py create_tenant_advanced "Docker Tenant" docker admin@docker.com \
    --database-host "localhost" \
    --database-port 5433 \
    --database-user "postgres" \
    --database-password "postgres" \
    --database-name "docker_tenant"
```

## 🔒 Security Configurations

### Encrypted Connections (Production)

```bash
# Main database with SSL
export DATABASE_URL="postgresql://admin:secure@main-db.com:5432/sales_main?sslmode=require"

# Tenant with SSL and client certificates
python manage.py create_tenant_advanced "SecureCorp" securecorp admin@securecorp.com \
    --database-url "postgresql://securecorp:ultra_secure@secure-db.com:5432/securecorp_db?sslmode=require&sslcert=/path/to/client.crt&sslkey=/path/to/client.key"
```

### Connection Pooling with PgBouncer

```bash
# Using PgBouncer for connection pooling
python manage.py create_tenant_advanced "PooledCorp" pooledcorp admin@pooledcorp.com \
    --database-host "pgbouncer.internal.com" \
    --database-port 6432 \
    --database-user "pooledcorp" \
    --database-password "pooled_pass" \
    --database-name "pooledcorp_db"
```

## 📊 Monitoring and Maintenance

### Database Health Checks

```bash
# Test all tenant database connections
python manage.py test_tenant_connections

# Test specific tenant
python manage.py test_tenant_connections --tenant demo --verbose

# Check tenant database status in Django admin
# Navigate to: http://admin.yourapp.com/admin/tenants/tenant/
```

### Database Migrations

```bash
# Apply new migration to all tenants
python manage.py makemigrations sales_app
python manage.py migrate_tenants --app sales_app

# Apply migration to specific tenant
python manage.py migrate_tenants --tenant bigcorp --app accounting_app

# Check migration status
python manage.py showmigrations --database sales_bigcorp
```

### Backup Strategies

```bash
# Automated backup script example
#!/bin/bash
for tenant in $(python manage.py list_tenants --active-only | grep -v "Name:" | awk '{print $3}'); do
    pg_dump -h localhost -U postgres sales_$tenant > /backups/sales_${tenant}_$(date +%Y%m%d).sql
    echo "Backed up tenant: $tenant"
done
```

## 🚀 Migration Examples

### Moving Tenant to Different Server

```bash
# Migrate tenant from shared server to dedicated server
python manage.py migrate_tenant_database bigcorp \
    --new-database-url "postgresql://bigcorp:ultra_secure@bigcorp-dedicated.com:5432/bigcorp_production" \
    --backup-current \
    --migrate-data
```

### Upgrading Database Engine

```bash
# Example: Moving from PostgreSQL 12 to 13
# 1. Setup new PostgreSQL 13 server
# 2. Migrate tenant
python manage.py migrate_tenant_database modernco \
    --new-database-url "postgresql://modernco:secure@pg13-server.com:5432/modernco_db" \
    --backup-current \
    --migrate-data
```

## 📈 Scaling Patterns

### Tenant Distribution Strategy

```bash
# Small tenants (< 10 users) - Shared server
python manage.py create_tenant "Small Co 1" small1 admin@small1.com --max-users 10
python manage.py create_tenant "Small Co 2" small2 admin@small2.com --max-users 10

# Medium tenants (10-100 users) - Shared powerful server  
python manage.py create_tenant_advanced "Medium Co" medium admin@medium.com \
    --database-host "powerful-shared.com" \
    --max-users 100

# Large tenants (100+ users) - Dedicated server
python manage.py create_tenant_advanced "Large Corp" large admin@large.com \
    --database-url "postgresql://large:secure@large-dedicated.com:5432/large_production" \
    --max-users 500
```

### Auto-scaling with Cloud Services

```bash
# Using managed database services that auto-scale
python manage.py create_tenant_advanced "CloudNative Co" cloudnative admin@cloudnative.com \
    --database-url "postgresql://cloudnative:secure@aurora-serverless.cluster-xyz.amazonaws.com:5432/cloudnative_db"
```

This comprehensive setup allows you to start simple and scale up as your tenant base grows!
