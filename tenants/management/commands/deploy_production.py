from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.conf import settings
import os


class Command(BaseCommand):
    help = 'Prepare system for production deployment'

    def add_arguments(self, parser):
        parser.add_argument(
            '--create-sample-tenant',
            action='store_true',
            help='Create a sample tenant for testing'
        )

    def handle(self, *args, **options):
        self.stdout.write("🚀 Preparing for production deployment...")
        
        # 1. Set up main database
        self.stdout.write("\n1️⃣ Setting up main database...")
        call_command('setup_main_database')
        
        # 2. Check database configuration
        self.stdout.write("\n2️⃣ Checking database configuration...")
        self.check_database_config()
        
        # 3. Check environment variables
        self.stdout.write("\n3️⃣ Checking environment variables...")
        self.check_environment_variables()
        
        # 4. Create sample tenant if requested
        if options['create_sample_tenant']:
            self.stdout.write("\n4️⃣ Creating sample tenant...")
            try:
                call_command(
                    'create_tenant',
                    'Sample Company',
                    'sample',
                    'admin@sample.com',
                    '--max-users=10'
                )
            except Exception as e:
                self.stdout.write(self.style.WARNING(f"Sample tenant creation failed: {e}"))
        
        # 5. Production checklist
        self.stdout.write("\n5️⃣ Production deployment checklist:")
        self.display_production_checklist()
        
        self.stdout.write(self.style.SUCCESS("\n✅ Production setup completed!"))

    def check_database_config(self):
        """Check database configuration"""
        try:
            default_db = settings.DATABASES['default']
            self.stdout.write(f"   Database Engine: {default_db['ENGINE']}")
            
            if 'sqlite' in default_db['ENGINE']:
                self.stdout.write("   ⚠️  Using SQLite (suitable for development)")
                self.stdout.write("   📝 For production, consider PostgreSQL or MySQL")
            else:
                self.stdout.write("   ✅ Using production database engine")
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"   ❌ Database config error: {e}"))

    def check_environment_variables(self):
        """Check critical environment variables"""
        required_vars = {
            'SECRET_KEY': 'Django secret key',
            'DEBUG': 'Debug mode setting',
        }
        
        optional_vars = {
            'DATABASE_URL': 'Database connection URL',
            'ALLOWED_HOSTS': 'Allowed hosts for production',
        }
        
        self.stdout.write("   Required variables:")
        for var, description in required_vars.items():
            value = os.environ.get(var)
            if value:
                self.stdout.write(f"   ✅ {var}: {description}")
            else:
                self.stdout.write(self.style.ERROR(f"   ❌ {var}: Missing - {description}"))
        
        self.stdout.write("   Optional variables:")
        for var, description in optional_vars.items():
            value = os.environ.get(var)
            if value:
                self.stdout.write(f"   ✅ {var}: {description}")
            else:
                self.stdout.write(self.style.WARNING(f"   ⚠️  {var}: Not set - {description}"))

    def display_production_checklist(self):
        """Display production deployment checklist"""
        checklist = [
            "🔒 Set DEBUG=False in production",
            "🔑 Generate new SECRET_KEY for production",
            "🌐 Configure proper ALLOWED_HOSTS",
            "💾 Set up production database (PostgreSQL/MySQL)",
            "📁 Configure static files serving (WhiteNoise/CDN)",
            "📧 Set up email backend (SMTP/SendGrid)",
            "🔐 Configure HTTPS/SSL certificates",
            "📊 Set up monitoring and logging",
            "💾 Configure automated backups",
            "🚀 Use production WSGI server (Gunicorn/uWSGI)",
            "🔄 Set up reverse proxy (Nginx/Apache)",
            "🔒 Change default tenant passwords",
            "👥 Configure proper user groups and permissions",
            "🏢 Set up proper domain names (not .localhost)",
            "📋 Test tenant creation and access",
        ]
        
        for item in checklist:
            self.stdout.write(f"   {item}")
        
        self.stdout.write("\n📚 Additional resources:")
        self.stdout.write("   - Django deployment checklist: https://docs.djangoproject.com/en/stable/howto/deployment/checklist/")
        self.stdout.write("   - Multi-tenant best practices: Check project documentation")
        self.stdout.write("   - Security guidelines: https://docs.djangoproject.com/en/stable/topics/security/")
