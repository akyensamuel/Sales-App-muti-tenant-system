#!/usr/bin/env python
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sales_management_project.settings')
sys.path.append('d:\\code\\Sales_App\\sales_management_project')
django.setup()

from django.test import Client
from django.contrib.auth.models import User

print("=== Testing Django Template Rendering for Charts ===")
print()

# Create a test client
client = Client()

# Create a test user or use an existing one
try:
    user = User.objects.first()
    if user:
        print(f"✅ Using existing user: {user.username}")
        # Login the user
        client.force_login(user)
    else:
        print("❌ No users found in database")
        user = User.objects.create_user('testuser', 'test@example.com', 'testpass')
        client.force_login(user)
        print("✅ Created and logged in test user")
        
except Exception as e:
    print(f"❌ Error with user authentication: {e}")

# Test the revenue tracking page
try:
    print("🔄 Requesting revenue tracking page...")
    response = client.get('/accounting/revenue-tracking/', follow=True)
    print(f"✅ Request successful - Status code: {response.status_code}")
    print(f"📍 Final URL: {response.request.get('PATH_INFO', 'Unknown')}")
    
    if response.status_code == 200:
        content = response.content.decode('utf-8')
        
        print("\n📊 Checking REVENUE chart elements:")
        
        revenue_checks = [
            ('Chart.js script', 'chart.js' in content.lower()),
            ('Canvas element', 'revenueChart' in content),
            ('Chart constructor', 'new Chart(' in content),
            ('Monthly data', 'monthly_data' in content),
            ('July 2025 label', 'July 2025' in content),
            ('Revenue value', '20371' in content),
            ('DOM ready listener', 'DOMContentLoaded' in content),
            ('Canvas reuse fix', 'revenueChartInstance' in content),
        ]
        
        for check_name, result in revenue_checks:
            status = "✅" if result else "❌"
            print(f"  {status} {check_name}: {'Found' if result else 'Not found'}")
        
        # Save rendered content for inspection
        with open('rendered_revenue_page.html', 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"\n📄 Revenue page HTML saved to 'rendered_revenue_page.html'")
        
    else:
        print(f"❌ Unexpected status code: {response.status_code}")

except Exception as e:
    print(f"❌ Error requesting revenue page: {e}")

# Test the profit & loss report page
try:
    print("\n🔄 Requesting profit & loss report page...")
    response = client.get('/accounting/profit-loss-report/', follow=True)
    print(f"✅ Request successful - Status code: {response.status_code}")
    
    if response.status_code == 200:
        content = response.content.decode('utf-8')
        
        print("\n📊 Checking EXPENSE chart elements:")
        
        expense_checks = [
            ('Chart.js script', 'chart.js' in content.lower()),
            ('Canvas element', 'expenseChart' in content),
            ('Chart constructor', 'new Chart(' in content),
            ('Expense data', 'expense_data' in content),
            ('Utilities category', 'Utilities' in content),
            ('DOM ready listener', 'DOMContentLoaded' in content),
            ('Canvas reuse fix', 'expenseChartInstance' in content),
            ('Doughnut chart type', 'doughnut' in content),
        ]
        
        for check_name, result in expense_checks:
            status = "✅" if result else "❌"
            print(f"  {status} {check_name}: {'Found' if result else 'Not found'}")
        
        # Save rendered content for inspection
        with open('rendered_expense_page.html', 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"\n📄 Expense page HTML saved to 'rendered_expense_page.html'")
        
    else:
        print(f"❌ Unexpected status code: {response.status_code}")
        
except Exception as e:
    print(f"❌ Error requesting expense page: {e}")
    import traceback
    traceback.print_exc()
