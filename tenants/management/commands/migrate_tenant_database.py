from django.core.management.base import BaseCommand, CommandError
from django.core.management import call_command
from django.db import connections
from tenants.models import Tenant
from django.conf import settings
import dj_database_url


class Command(BaseCommand):
    help = 'Migrate tenant database to new server/configuration'
    
    def add_arguments(self, parser):
        parser.add_argument('subdomain', help='Tenant subdomain to migrate')
        
        parser.add_argument(
            '--new-database-url',
            required=True,
            help='New database URL (postgresql://user:pass@host:port/dbname)'
        )
        
        parser.add_argument(
            '--backup-current',
            action='store_true',
            help='Create backup of current database before migration'
        )
        
        parser.add_argument(
            '--migrate-data',
            action='store_true',
            help='Migrate existing data to new database'
        )
        
        parser.add_argument(
            '--backup-path',
            default='/tmp/',
            help='Path to store database backup (default: /tmp/)'
        )
        
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show migration plan without executing'
        )
    
    def handle(self, *args, **options):
        subdomain = options['subdomain']
        new_database_url = options['new_database_url']
        
        # Get tenant
        try:
            tenant = Tenant.objects.get(subdomain=subdomain)
        except Tenant.DoesNotExist:
            raise CommandError(f'Tenant "{subdomain}" not found')
        
        # Parse new database configuration
        try:
            new_config = dj_database_url.parse(new_database_url)
        except Exception as e:
            raise CommandError(f'Invalid database URL: {e}')
        
        current_database = tenant.database_name
        new_database_name = new_config['NAME']
        
        self.stdout.write('\n' + '='*60)
        self.stdout.write(f'Database Migration Plan for: {tenant.name}')
        self.stdout.write(f'Subdomain: {subdomain}')
        self.stdout.write(f'Current Database: {current_database}')
        self.stdout.write(f'New Database: {new_database_name}')
        self.stdout.write(f'New Host: {new_config.get("HOST", "localhost")}')
        self.stdout.write(f'New Port: {new_config.get("PORT", "5432")}')
        self.stdout.write('='*60)
        
        if options['dry_run']:
            self.stdout.write(self.style.WARNING('\nDRY RUN - No changes will be made'))
            self._show_migration_steps(options)
            return
        
        # Confirm migration
        confirm = input('\nProceed with database migration? (yes/no): ')
        if confirm.lower() != 'yes':
            self.stdout.write('Migration cancelled')
            return
        
        try:
            # Step 1: Backup current database
            if options['backup_current']:
                self.stdout.write('\n1. Creating backup of current database...')
                backup_file = self._backup_database(tenant, options['backup_path'])
                self.stdout.write(f'   Backup saved to: {backup_file}')
            
            # Step 2: Create new database
            self.stdout.write('\n2. Setting up new database...')
            settings.DATABASES[f'new_{current_database}'] = new_config
            
            # Step 3: Run migrations on new database
            self.stdout.write('\n3. Running migrations on new database...')
            call_command('migrate', database=f'new_{current_database}', verbosity=1)
            
            # Step 4: Migrate data if requested
            if options['migrate_data']:
                self.stdout.write('\n4. Migrating data to new database...')
                self._migrate_data(current_database, f'new_{current_database}')
            
            # Step 5: Update tenant configuration
            self.stdout.write('\n5. Updating tenant configuration...')
            tenant.database_name = new_database_name
            tenant.save()
            
            # Step 6: Update Django settings
            settings.DATABASES[new_database_name] = new_config
            del settings.DATABASES[current_database]
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'\n✅ Successfully migrated tenant "{tenant.name}" to new database'
                )
            )
            self.stdout.write(f'🔗 New database: {new_database_name}')
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'\n❌ Migration failed: {str(e)}')
            )
            # Cleanup on failure
            try:
                if f'new_{current_database}' in settings.DATABASES:
                    del settings.DATABASES[f'new_{current_database}']
            except:
                pass
            raise CommandError(f'Database migration failed: {str(e)}')
    
    def _show_migration_steps(self, options):
        """Show what the migration would do"""
        steps = [
            "1. Create backup of current database" if options['backup_current'] else None,
            "2. Create and configure new database",
            "3. Run Django migrations on new database", 
            "4. Copy data from old to new database" if options['migrate_data'] else None,
            "5. Update tenant configuration",
            "6. Update Django database settings"
        ]
        
        self.stdout.write('\nMigration Steps:')
        for i, step in enumerate([s for s in steps if s], 1):
            self.stdout.write(f'  {step}')
    
    def _backup_database(self, tenant, backup_path):
        """Create backup of current tenant database"""
        import subprocess
        import os
        from datetime import datetime
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_filename = f'{tenant.subdomain}_backup_{timestamp}.sql'
        backup_file = os.path.join(backup_path, backup_filename)
        
        # Get current database configuration
        current_db = settings.DATABASES[tenant.database_name]
        
        if 'postgresql' in current_db['ENGINE']:
            cmd = [
                'pg_dump',
                '-h', current_db.get('HOST', 'localhost'),
                '-p', str(current_db.get('PORT', 5432)),
                '-U', current_db.get('USER', ''),
                '-d', current_db['NAME'],
                '-f', backup_file
            ]
            
            # Set password via environment variable
            env = os.environ.copy()
            if current_db.get('PASSWORD'):
                env['PGPASSWORD'] = current_db['PASSWORD']
            
            subprocess.run(cmd, env=env, check=True)
            
        else:
            raise CommandError('Backup only supported for PostgreSQL databases')
        
        return backup_file
    
    def _migrate_data(self, old_db, new_db):
        """Migrate data from old database to new database"""
        from django.core.management import call_command
        import tempfile
        import os
        
        # Create temporary dump file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            dump_file = f.name
        
        try:
            # Export data from old database
            self.stdout.write('   Exporting data from current database...')
            call_command(
                'dumpdata',
                '--database', old_db,
                '--exclude', 'contenttypes',
                '--exclude', 'auth.permission',
                '--output', dump_file,
                verbosity=0
            )
            
            # Import data to new database
            self.stdout.write('   Importing data to new database...')
            call_command(
                'loaddata',
                dump_file,
                '--database', new_db,
                verbosity=0
            )
            
        finally:
            # Clean up temporary file
            try:
                os.unlink(dump_file)
            except:
                pass
