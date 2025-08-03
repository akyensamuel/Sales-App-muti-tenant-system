from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group
from django.core.management import call_command


class Command(BaseCommand):
    help = 'Clean main database to only contain tenant configs and groups'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force cleanup without confirmation'
        )

    def handle(self, *args, **options):
        if not options['force']:
            confirm = input(
                "⚠️  This will remove all user accounts from the main database. "
                "User accounts should exist in tenant databases only. Continue? (y/N): "
            )
            if confirm.lower() != 'y':
                self.stdout.write("Operation cancelled.")
                return

        self.stdout.write("🧹 Cleaning up main database...")
        
        # Remove all users from main database
        user_count = User.objects.count()
        if user_count > 0:
            self.stdout.write(f"   Removing {user_count} users from main database...")
            User.objects.all().delete()
            self.stdout.write(self.style.SUCCESS(f"   ✅ Removed {user_count} users"))
        else:
            self.stdout.write("   ℹ️  No users found in main database")
        
        # Ensure default groups exist
        self.stdout.write("   Creating/updating default groups...")
        default_groups = ['Admin', 'Managers', 'Cashiers']
        
        for group_name in default_groups:
            group, created = Group.objects.get_or_create(name=group_name)
            if created:
                self.stdout.write(f"   ✅ Created group: {group_name}")
            else:
                self.stdout.write(f"   ℹ️  Group exists: {group_name}")
        
        # Verify main database state
        self.stdout.write("\n📊 Main database summary:")
        self.stdout.write(f"   Users: {User.objects.count()} (should be 0)")
        self.stdout.write(f"   Groups: {Group.objects.count()} (should be 3)")
        
        from tenants.models import Tenant
        tenant_count = Tenant.objects.count()
        self.stdout.write(f"   Tenants: {tenant_count}")
        
        if tenant_count > 0:
            self.stdout.write("\n🏢 Configured tenants:")
            for tenant in Tenant.objects.all():
                self.stdout.write(f"   - {tenant.name} ({tenant.subdomain})")
        
        self.stdout.write(self.style.SUCCESS("\n✅ Main database cleanup completed!"))
        self.stdout.write("\nMain database now contains:")
        self.stdout.write("  ✓ Tenant configurations and database URLs")
        self.stdout.write("  ✓ Default groups (Admin, Managers, Cashiers)")
        self.stdout.write("  ✓ NO user accounts")
        self.stdout.write("\nAll user accounts should be in tenant databases.")
