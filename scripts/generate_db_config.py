#!/usr/bin/env python3
"""
Database Configuration Generator for Multi-Tenant Sales Management System

This script helps generate environment variables and configuration files
for different deployment scenarios.
"""

import os
import argparse
import json
from urllib.parse import urlparse


class DatabaseConfigGenerator:
    def __init__(self):
        self.config = {}
    
    def generate_single_server_config(self, host='localhost', port=5432, user='postgres', password='postgres'):
        """Generate config for single-server multi-database setup"""
        return {
            'DATABASE_URL': f'postgresql://{user}:{password}@{host}:{port}/sales_main',
            'TENANT_DATABASE_TEMPLATE': {
                'ENGINE': 'django.db.backends.postgresql',
                'HOST': host,
                'PORT': port,
                'USER': user,
                'PASSWORD': password,
                'OPTIONS': {'charset': 'utf8mb4'}
            }
        }
    
    def generate_aws_rds_config(self, main_endpoint, username, password, region='us-east-1'):
        """Generate config for AWS RDS deployment"""
        return {
            'DATABASE_URL': f'postgresql://{username}:{password}@{main_endpoint}:5432/sales_main',
            'TENANT_DATABASE_TEMPLATE': {
                'ENGINE': 'django.db.backends.postgresql',
                'HOST': main_endpoint,
                'PORT': 5432,
                'USER': username,
                'PASSWORD': password,
                'OPTIONS': {
                    'charset': 'utf8mb4',
                    'sslmode': 'require'
                }
            },
            'AWS_REGION': region
        }
    
    def generate_gcp_sql_config(self, project_id, region, instance_name, username, password):
        """Generate config for Google Cloud SQL"""
        connection_name = f'{project_id}:{region}:{instance_name}'
        return {
            'DATABASE_URL': f'postgresql://{username}:{password}@/sales_main?host=/cloudsql/{connection_name}',
            'TENANT_DATABASE_TEMPLATE': {
                'ENGINE': 'django.db.backends.postgresql',
                'HOST': f'/cloudsql/{connection_name}',
                'USER': username,
                'PASSWORD': password,
                'OPTIONS': {'charset': 'utf8mb4'}
            },
            'GCP_PROJECT_ID': project_id
        }
    
    def generate_azure_config(self, server_name, username, password, resource_group):
        """Generate config for Azure Database for PostgreSQL"""
        host = f'{server_name}.postgres.database.azure.com'
        full_username = f'{username}@{server_name}'
        return {
            'DATABASE_URL': f'postgresql://{full_username}:{password}@{host}:5432/sales_main',
            'TENANT_DATABASE_TEMPLATE': {
                'ENGINE': 'django.db.backends.postgresql',
                'HOST': host,
                'PORT': 5432,
                'USER': full_username,
                'PASSWORD': password,
                'OPTIONS': {
                    'charset': 'utf8mb4',
                    'sslmode': 'require'
                }
            },
            'AZURE_RESOURCE_GROUP': resource_group
        }
    
    def generate_docker_config(self, main_port=5432, tenant_port=5433):
        """Generate config for Docker Compose setup"""
        return {
            'DATABASE_URL': f'postgresql://postgres:postgres@localhost:{main_port}/sales_main',
            'TENANT_DATABASE_TEMPLATE': {
                'ENGINE': 'django.db.backends.postgresql',
                'HOST': 'localhost',
                'PORT': tenant_port,
                'USER': 'postgres',
                'PASSWORD': 'postgres',
                'OPTIONS': {'charset': 'utf8mb4'}
            }
        }
    
    def generate_env_file(self, config, filename='.env'):
        """Generate .env file from configuration"""
        with open(filename, 'w') as f:
            f.write("# Multi-Tenant Sales Management System Configuration\n")
            f.write("# Generated automatically - modify as needed\n\n")
            
            for key, value in config.items():
                if isinstance(value, dict):
                    # Skip complex objects for .env file
                    continue
                f.write(f'{key}={value}\n')
            
            f.write('\n# Additional settings\n')
            f.write('DEBUG=False\n')
            f.write('ALLOWED_HOSTS=.yourdomain.com,yourdomain.com\n')
            f.write('SECRET_KEY=your-secret-key-here\n')
    
    def generate_docker_compose(self, filename='docker-compose.yml'):
        """Generate Docker Compose file for development"""
        compose_content = '''version: '3.8'

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
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 30s
      timeout: 10s
      retries: 3

  tenant-db:
    image: postgres:13
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    ports:
      - "5433:5432"
    volumes:
      - tenant_db_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 30s
      timeout: 10s
      retries: 3

  web:
    build: .
    ports:
      - "8000:8000"
    depends_on:
      - main-db
      - tenant-db
    environment:
      - DATABASE_URL=postgresql://postgres:postgres@main-db:5432/sales_main
    volumes:
      - .:/app

volumes:
  main_db_data:
  tenant_db_data:
'''
        with open(filename, 'w') as f:
            f.write(compose_content)
    
    def generate_tenant_creation_script(self, tenants_config, filename='create_tenants.sh'):
        """Generate shell script to create multiple tenants"""
        with open(filename, 'w') as f:
            f.write('#!/bin/bash\n')
            f.write('# Auto-generated tenant creation script\n\n')
            f.write('set -e  # Exit on any error\n\n')
            
            for tenant in tenants_config:
                name = tenant['name']
                subdomain = tenant['subdomain']
                email = tenant['email']
                max_users = tenant.get('max_users', 50)
                
                # Basic tenant creation
                if 'database_url' in tenant:
                    f.write(f'echo "Creating tenant: {name}"\n')
                    f.write(f'python manage.py create_tenant_advanced "{name}" {subdomain} {email} \\\n')
                    f.write(f'    --database-url "{tenant["database_url"]}" \\\n')
                    f.write(f'    --max-users {max_users}\n\n')
                else:
                    f.write(f'echo "Creating tenant: {name}"\n')
                    f.write(f'python manage.py create_tenant "{name}" {subdomain} {email} \\\n')
                    f.write(f'    --max-users {max_users}\n\n')
            
            f.write('echo "All tenants created successfully!"\n')
        
        # Make script executable
        os.chmod(filename, 0o755)
    
    def print_config_summary(self, config):
        """Print configuration summary"""
        print("\n" + "="*60)
        print("CONFIGURATION SUMMARY")
        print("="*60)
        
        if 'DATABASE_URL' in config:
            parsed = urlparse(config['DATABASE_URL'])
            print(f"Main Database:")
            print(f"  Host: {parsed.hostname}")
            print(f"  Port: {parsed.port}")
            print(f"  Database: {parsed.path[1:]}")  # Remove leading /
            print(f"  User: {parsed.username}")
        
        if 'TENANT_DATABASE_TEMPLATE' in config:
            template = config['TENANT_DATABASE_TEMPLATE']
            print(f"\nTenant Database Template:")
            print(f"  Engine: {template.get('ENGINE', 'Not specified')}")
            print(f"  Host: {template.get('HOST', 'Not specified')}")
            print(f"  Port: {template.get('PORT', 'Not specified')}")
        
        print("\nGenerated Files:")
        if os.path.exists('.env'):
            print("  ✓ .env (environment variables)")
        if os.path.exists('docker-compose.yml'):
            print("  ✓ docker-compose.yml (Docker setup)")
        if os.path.exists('create_tenants.sh'):
            print("  ✓ create_tenants.sh (tenant creation script)")


def main():
    parser = argparse.ArgumentParser(description='Generate database configuration for multi-tenant deployment')
    parser.add_argument('--platform', choices=['local', 'aws', 'gcp', 'azure', 'docker'], 
                       default='local', help='Target platform')
    parser.add_argument('--output-dir', default='.', help='Output directory for generated files')
    
    # Common options
    parser.add_argument('--host', default='localhost', help='Database host')
    parser.add_argument('--port', type=int, default=5432, help='Database port')
    parser.add_argument('--username', default='postgres', help='Database username')
    parser.add_argument('--password', default='postgres', help='Database password')
    
    # AWS specific
    parser.add_argument('--aws-region', default='us-east-1', help='AWS region')
    parser.add_argument('--rds-endpoint', help='RDS endpoint')
    
    # GCP specific
    parser.add_argument('--gcp-project', help='GCP project ID')
    parser.add_argument('--gcp-region', default='us-central1', help='GCP region')
    parser.add_argument('--gcp-instance', help='Cloud SQL instance name')
    
    # Azure specific
    parser.add_argument('--azure-server', help='Azure PostgreSQL server name')
    parser.add_argument('--azure-resource-group', help='Azure resource group')
    
    args = parser.parse_args()
    
    generator = DatabaseConfigGenerator()
    
    # Change to output directory
    if args.output_dir != '.':
        os.makedirs(args.output_dir, exist_ok=True)
        os.chdir(args.output_dir)
    
    # Generate configuration based on platform
    if args.platform == 'local':
        config = generator.generate_single_server_config(
            args.host, args.port, args.username, args.password
        )
    elif args.platform == 'aws':
        if not args.rds_endpoint:
            print("Error: --rds-endpoint required for AWS platform")
            return
        config = generator.generate_aws_rds_config(
            args.rds_endpoint, args.username, args.password, args.aws_region
        )
    elif args.platform == 'gcp':
        if not all([args.gcp_project, args.gcp_instance]):
            print("Error: --gcp-project and --gcp-instance required for GCP platform")
            return
        config = generator.generate_gcp_sql_config(
            args.gcp_project, args.gcp_region, args.gcp_instance, args.username, args.password
        )
    elif args.platform == 'azure':
        if not all([args.azure_server, args.azure_resource_group]):
            print("Error: --azure-server and --azure-resource-group required for Azure platform")
            return
        config = generator.generate_azure_config(
            args.azure_server, args.username, args.password, args.azure_resource_group
        )
    elif args.platform == 'docker':
        config = generator.generate_docker_config()
        generator.generate_docker_compose()
    
    # Generate files
    generator.generate_env_file(config)
    
    # Generate sample tenant creation script
    sample_tenants = [
        {'name': 'Demo Company', 'subdomain': 'demo', 'email': 'admin@demo.com'},
        {'name': 'Test Company', 'subdomain': 'test', 'email': 'admin@test.com'},
    ]
    generator.generate_tenant_creation_script(sample_tenants)
    
    # Print summary
    generator.print_config_summary(config)
    
    print(f"\nNext steps:")
    print(f"1. Review and modify .env file with your actual credentials")
    print(f"2. Set your SECRET_KEY and ALLOWED_HOSTS in .env")
    print(f"3. Run: python manage.py migrate")
    print(f"4. Run: ./create_tenants.sh to create sample tenants")
    
    if args.platform == 'docker':
        print(f"5. For Docker: run 'docker-compose up -d' to start databases")


if __name__ == '__main__':
    main()
