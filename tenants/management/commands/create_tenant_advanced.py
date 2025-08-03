from django.core.management.base import BaseCommand, CommandError
from django.db import connection
from django.core.management import call_command
from tenants.models import Tenant
from django.conf import settings
import dj_database_url


class Command(BaseCommand):
    help = 'Create a new tenant with advanced database configuration options'
    
    def add_arguments(self, parser):
        parser.add_argument('name', type=str, help='Organization name')
        parser.add_argument('subdomain', type=str, help='Subdomain for tenant')
        parser.add_argument('admin_email', type=str, help='Admin email address')
        
        parser.add_argument(
            '--max-users',
            type=int,
            default=50,
            help='Maximum number of users (default: 50)'
        )
        
        parser.add_argument(
            '--multi-location',
            action='store_true',
            help='Enable multi-location support'
        )
        
        # Advanced database configuration options
        parser.add_argument(
            '--database-url',
            help='Complete database URL (e.g., postgresql://user:pass@host:port/dbname)'
        )
        
        parser.add_argument(
            '--database-host',
            help='Database host (overrides template)'
        )
        
        parser.add_argument(
            '--database-port',
            type=int,
            help='Database port (overrides template)'
        )
        
        parser.add_argument(
            '--database-user',
            help='Database username (overrides template)'
        )
        
        parser.add_argument(
            '--database-password',
            help='Database password (overrides template)'
        )
        
        parser.add_argument(
            '--database-name',
            help='Custom database name (default: auto-generated as sales_{subdomain})'
        )
        
        parser.add_argument(
            '--database-engine',
            choices=['postgresql', 'mysql', 'sqlite3'],
            default='postgresql',
            help='Database engine (default: postgresql)'
        )
        
        parser.add_argument(
            '--skip-database-creation',
            action='store_true',
            help='Skip database creation (assumes database already exists)'
        )
        
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show configuration without creating tenant'
        )
    
    def handle(self, *args, **options):
        name = options['name']
        subdomain = options['subdomain']
        admin_email = options['admin_email']
        max_users = options['max_users']
        multi_location = options['multi_location']
        
        # Validate subdomain
        if Tenant.objects.filter(subdomain=subdomain).exists():
            raise CommandError(f'Tenant with subdomain "{subdomain}" already exists')
        
        # Determine database configuration
        database_config = self._get_database_config(options)
        database_name = options['database_name'] or f"sales_{options['subdomain']}"
        
        # Show configuration
        self.stdout.write('\n' + '='*60)
        self.stdout.write(f'Tenant Configuration:')
        self.stdout.write(f'  Name: {name}')
        self.stdout.write(f'  Subdomain: {subdomain}')
        self.stdout.write(f'  Admin Email: {admin_email}')
        self.stdout.write(f'  Max Users: {max_users}')
        self.stdout.write(f'  Multi-Location: {"Yes" if multi_location else "No"}')
        self.stdout.write(f'\nDatabase Configuration:')
        self.stdout.write(f'  Engine: {database_config["ENGINE"]}')
        self.stdout.write(f'  Database: {database_name}')
        if 'HOST' in database_config:
            self.stdout.write(f'  Host: {database_config["HOST"]}')
        if 'PORT' in database_config:
            self.stdout.write(f'  Port: {database_config["PORT"]}')
        if 'USER' in database_config:
            self.stdout.write(f'  User: {database_config["USER"]}')
        self.stdout.write('='*60)
        
        if options['dry_run']:
            self.stdout.write(self.style.WARNING('DRY RUN - No changes made'))
            return
        
        # Create tenant record
        self.stdout.write(f'\nCreating tenant: {name}...')
        
        # Prepare tenant data
        tenant_data = {
            'name': name,
            'subdomain': subdomain,
            'admin_email': admin_email,
            'max_users': max_users,
            'supports_multi_location': multi_location,
            'database_name': database_name,
            'database_engine': database_config['ENGINE'],
        }
        
        # Add optional database configuration
        if options.get('database_url'):
            tenant_data['database_url'] = options['database_url']
        if database_config.get('HOST'):
            tenant_data['database_host'] = database_config['HOST']
        if database_config.get('PORT'):
            tenant_data['database_port'] = database_config['PORT']
        if database_config.get('USER'):
            tenant_data['database_user'] = database_config['USER']
        if database_config.get('PASSWORD'):
            tenant_data['database_password'] = database_config['PASSWORD']
        
        tenant = Tenant.objects.create(**tenant_data)
        
        # Add tenant database to Django settings
        settings.DATABASES[database_name] = database_config
        
        try:
            # Create database (unless skipped)
            if not options['skip_database_creation']:
                self.stdout.write(f'Creating database: {database_name}...')
                self._create_database(database_config)
            
            # Run migrations for the new tenant database
            self.stdout.write(f'Running migrations for {database_name}...')
            call_command('migrate', database=database_name, verbosity=0)
            
            # Create initial data
            self.stdout.write('Creating initial data...')
            self._create_initial_data(tenant)
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'\n✅ Successfully created tenant "{name}" with subdomain "{subdomain}"'
                )
            )
            self.stdout.write(f'🌐 Access URL: http://{subdomain}.localhost:8000 (development)')
            self.stdout.write(f'📧 Admin Email: {admin_email}')
            
        except Exception as e:
            # Cleanup on failure
            self.stdout.write(
                self.style.ERROR(f'❌ Error creating tenant: {str(e)}')
            )
            # Delete tenant record
            tenant.delete()
            # Try to drop database if it was created
            try:
                if not options['skip_database_creation']:
                    self._drop_database(database_config)
            except:
                pass
            raise CommandError(f'Failed to create tenant: {str(e)}')
    
    def _get_database_config(self, options):
        """Generate database configuration based on options"""
        
        # If complete database URL provided, parse it
        if options['database_url']:
            config = dj_database_url.parse(options['database_url'])
            # Extract database name for our naming convention
            if not options['database_name']:
                options['database_name'] = config['NAME']
            return config
        
        # Start with template configuration or clean config
        if options['database_engine'] == 'sqlite3':
            # Start with clean config for SQLite
            config = {'ENGINE': 'django.db.backends.sqlite3'}
        else:
            config = getattr(settings, 'TENANT_DATABASE_TEMPLATE', {}).copy()
        
        # Set database engine
        engine_map = {
            'postgresql': 'django.db.backends.postgresql',
            'mysql': 'django.db.backends.mysql',
            'sqlite3': 'django.db.backends.sqlite3',
        }
        config['ENGINE'] = engine_map[options['database_engine']]
        
        # Set database name
        database_name = options['database_name'] or f"sales_{options['subdomain']}"
        config['NAME'] = database_name
        
        # Override with custom parameters
        if options['database_host']:
            config['HOST'] = options['database_host']
        elif 'HOST' not in config and options['database_engine'] != 'sqlite3':
            config['HOST'] = 'localhost'
            
        if options['database_port']:
            config['PORT'] = options['database_port']
        elif 'PORT' not in config and options['database_engine'] == 'postgresql':
            config['PORT'] = 5432
        elif 'PORT' not in config and options['database_engine'] == 'mysql':
            config['PORT'] = 3306
            
        if options['database_user']:
            config['USER'] = options['database_user']
            
        if options['database_password']:
            config['PASSWORD'] = options['database_password']
        
        # Special handling for SQLite
        if options['database_engine'] == 'sqlite3':
            if not options['database_name']:
                config['NAME'] = f"{settings.BASE_DIR}/tenant_dbs/{database_name}.sqlite3"
            else:
                config['NAME'] = f"{settings.BASE_DIR}/tenant_dbs/{options['database_name']}.sqlite3"
            # Remove unnecessary keys for SQLite
            config.pop('HOST', None)
            config.pop('PORT', None)
            config.pop('USER', None)
            config.pop('PASSWORD', None)
            # Ensure essential SQLite settings
            config.setdefault('OPTIONS', {})
        
        return config
    
    def _create_database(self, database_config):
        """Create the database for the tenant"""
        engine = database_config['ENGINE']
        database_name = database_config['NAME']
        
        if 'postgresql' in engine:
            self._create_postgresql_database(database_config)
        elif 'mysql' in engine:
            self._create_mysql_database(database_config)
        elif 'sqlite3' in engine:
            # SQLite databases are created automatically
            pass
        else:
            raise CommandError(f"Unsupported database engine: {engine}")
    
    def _create_postgresql_database(self, config):
        """Create PostgreSQL database"""
        database_name = config['NAME']
        
        # Use default connection to create new database
        with connection.cursor() as cursor:
            cursor.execute(f'CREATE DATABASE "{database_name}"')
    
    def _create_mysql_database(self, config):
        """Create MySQL database"""
        database_name = config['NAME']
        
        # Use default connection to create new database
        with connection.cursor() as cursor:
            cursor.execute(f'CREATE DATABASE `{database_name}`')
    
    def _drop_database(self, database_config):
        """Drop the database (for cleanup on error)"""
        engine = database_config['ENGINE']
        database_name = database_config['NAME']
        
        with connection.cursor() as cursor:
            if 'postgresql' in engine:
                cursor.execute(f'DROP DATABASE IF EXISTS "{database_name}"')
            elif 'mysql' in engine:
                cursor.execute(f'DROP DATABASE IF EXISTS `{database_name}`')
    
    def _create_initial_data(self, tenant):
        """Create initial data for the tenant"""
        # You can add initial data creation logic here
        # For example, create default user groups, categories, etc.
        self.stdout.write('  - Initial data setup complete')
