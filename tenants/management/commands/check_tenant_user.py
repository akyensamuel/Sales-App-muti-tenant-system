from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group
import sqlite3
import os

class Command(BaseCommand):
    help = 'Check user and group assignments in tenant SQLite database'

    def add_arguments(self, parser):
        parser.add_argument('subdomain', type=str, help='Tenant subdomain')

    def handle(self, *args, **options):
        subdomain = options['subdomain']
        
        # Direct SQLite connection
        db_path = os.path.join('tenant_dbs', f'sales_{subdomain}.sqlite3')
        
        if not os.path.exists(db_path):
            self.stdout.write(self.style.ERROR(f"Database file not found: {db_path}"))
            return
        
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Check if user exists
            cursor.execute("SELECT id, username, email, is_staff, is_superuser FROM auth_user WHERE username = 'Akyen'")
            user_result = cursor.fetchone()
            
            if user_result:
                user_id, username, email, is_staff, is_superuser = user_result
                self.stdout.write(f"👤 User found: {username}")
                self.stdout.write(f"   📧 Email: {email}")
                self.stdout.write(f"   🛡️  Staff: {'Yes' if is_staff else 'No'}")
                self.stdout.write(f"   👑 Superuser: {'Yes' if is_superuser else 'No'}")
                
                # Check groups
                cursor.execute("""
                    SELECT g.name 
                    FROM auth_group g
                    JOIN auth_user_groups ug ON g.id = ug.group_id
                    WHERE ug.user_id = ?
                """, (user_id,))
                
                groups = [row[0] for row in cursor.fetchall()]
                self.stdout.write(f"   👥 Groups: {', '.join(groups) if groups else 'None'}")
                
                # Check all available groups
                cursor.execute("SELECT name FROM auth_group")
                all_groups = [row[0] for row in cursor.fetchall()]
                self.stdout.write(f"   📋 Available groups: {', '.join(all_groups)}")
                
                # Check if user is in all required groups
                required_groups = ['Admin', 'Managers', 'Cashiers']
                missing_groups = [g for g in required_groups if g not in groups]
                
                if missing_groups:
                    self.stdout.write(self.style.WARNING(f"⚠️  Missing groups: {', '.join(missing_groups)}"))
                    
                    # Add missing groups
                    for group_name in missing_groups:
                        cursor.execute("SELECT id FROM auth_group WHERE name = ?", (group_name,))
                        group_result = cursor.fetchone()
                        if group_result:
                            group_id = group_result[0]
                            cursor.execute("INSERT OR IGNORE INTO auth_user_groups (user_id, group_id) VALUES (?, ?)", (user_id, group_id))
                            self.stdout.write(f"   ✅ Added user to group: {group_name}")
                    
                    conn.commit()
                    self.stdout.write(self.style.SUCCESS("✅ User now has all required groups!"))
                else:
                    self.stdout.write(self.style.SUCCESS("✅ User has all required groups!"))
                    
            else:
                self.stdout.write(self.style.ERROR("❌ User 'Akyen' not found"))
            
            conn.close()
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error: {str(e)}"))
