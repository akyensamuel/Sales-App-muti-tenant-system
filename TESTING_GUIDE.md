# Testing Guide - Multi-Tenant Sales Management System

## Quick Testing Setup

### 🚀 Start Development Server
```bash
python manage.py runserver
```

### 🏗️ Create Test Tenant
```bash
python manage.py create_tenant "Test Company" "test" "test@test.com"
```

### 🌐 Access Test Tenant
- **Main App**: `http://test.localhost:8000/`
- **Sales**: `http://test.localhost:8000/sales/`
- **Accounting**: `http://test.localhost:8000/accounting/`

### 🔑 Default Login
- **Username**: `Akyen`
- **Password**: `08000000`

---

## Multi-Tenant Testing

### ✅ Test Tenant Isolation
1. Create multiple tenants:
```bash
python manage.py create_tenant "Company A" "companya" "admin@companya.com"
python manage.py create_tenant "Company B" "companyb" "admin@companyb.com"
```

2. Verify separate data:
- Login to `http://companya.localhost:8000/`
- Create products, customers, sales
- Login to `http://companyb.localhost:8000/`
- Verify different data set

### ✅ Test Database Routing
1. Check main database (tenant configs only):
```bash
python manage.py setup_main_database
```

2. Check tenant database (all app data):
```bash
# Access any tenant subdomain and verify:
# - User authentication works
# - Products/customers/sales are isolated
# - Accounting data is separate
```

### ✅ Test Production Scenarios

#### External Database
```bash
python manage.py create_tenant "Prod Test" "prodtest" "admin@prod.com" \
  --database-url="postgresql://user:pass@external-host:5432/prodtest_db"
```

#### Force Migration (Troubleshooting)
```bash
python manage.py force_migrate_tenant "prodtest"
```

#### Manual Setup (Fallback)
```bash
python manage.py manual_setup_tenant "prodtest"
```

---

## Feature Testing

### 🛒 Sales App Testing
1. **Product Management**:
   - Add products with different categories
   - Test stock levels and validation
   - Verify price calculations

2. **Sales Entry**:
   - Create multi-item invoices
   - Test customer search/creation
   - Verify auto-save functionality
   - Test print receipts

3. **Invoice Management**:
   - View invoice details
   - Edit invoices (Manager role)
   - Cancel invoices and verify stock restoration

### 💰 Accounting App Testing
1. **Dashboard**:
   - Verify financial overview
   - Check KPI calculations
   - Test date range filtering

2. **Expense Management**:
   - Add expenses with categories
   - Upload receipts
   - Test bulk operations

3. **Reports**:
   - Generate P&L statements
   - Test revenue analysis
   - Verify outstanding invoice tracking

### 👥 User Management Testing
1. **Role-Based Access**:
   - Test Admin permissions (full access)
   - Test Manager permissions (no user management)
   - Test Cashier permissions (sales only)

2. **Authentication**:
   - Test login/logout functionality
   - Verify role-based redirects
   - Test session management

---

## Troubleshooting Tests

### 🔧 Common Issues

#### 1. Subdomain Not Working
**Problem**: `http://test.localhost:8000/` not resolving

**Solution**: Add to hosts file (`C:\Windows\System32\drivers\etc\hosts`):
```
127.0.0.1 test.localhost
127.0.0.1 demo.localhost
127.0.0.1 companya.localhost
127.0.0.1 companyb.localhost
```

#### 2. Database Connection Errors
**Problem**: `could not connect to server`

**Test Commands**:
```bash
# Test main database connection
python manage.py check

# Test tenant database connection
python manage.py migrate_tenant test

# Force reset if needed
python manage.py force_migrate_tenant test
```

#### 3. Migration State Issues
**Problem**: Tables don't exist but migrations show as applied

**Solution**:
```bash
python manage.py force_migrate_tenant test
```

#### 4. Permission Errors
**Problem**: Users can't access features

**Check**:
- Verify user is in correct groups (Admin, Managers, Cashiers)
- Test on fresh tenant with default user
- Check role-based navigation

---

## Performance Testing

### 📊 Load Testing
1. **Multiple Tenants**: Create 10+ tenants and test simultaneous access
2. **Database Performance**: Monitor query performance with Django Debug Toolbar
3. **Memory Usage**: Test with multiple tenant databases open

### 🔍 Security Testing
1. **Tenant Isolation**: Verify no cross-tenant data access
2. **URL Manipulation**: Test direct URL access to other tenants
3. **Authentication**: Test session security and proper logouts

---

## Automated Testing

### 🤖 Run Test Suite
```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test sales_app
python manage.py test accounting_app
python manage.py test tenants

# Run with coverage
coverage run --source='.' manage.py test
coverage report
```

### 📝 Test Categories
- **Unit Tests**: Model and form validation
- **Integration Tests**: Multi-tenant functionality
- **View Tests**: HTTP response and permission testing
- **Database Tests**: Multi-database routing and isolation

---

## 🚀 Quick Start

### Prerequisites
1. **Activate Virtual Environment:**
   ```cmd
   D:/code/Sales_App/virtual/Scripts/activate
   ```

2. **Navigate to Project Directory:**
   ```cmd
   cd "d:\code\Sales_App\sales_management_project"
   ```

3. **Python Command:**
   Use the full path: `"D:/code/Sales_App/virtual/Scripts/python.exe"`
   or the relative path on your local machine

## 📂 Test Categories

### 🔍 Functional Tests (`tests/functional/`)
**Purpose:** End-to-end testing of complete features and user workflows

**Available Tests:**
```cmd
# Test Chart.js rendering and functionality
"D:/code/Sales_App/virtual/Scripts/python.exe" tests/functional/test_django_chart.py

# Test print system with actual invoice data
"D:/code/Sales_App/virtual/Scripts/python.exe" tests/functional/test_print_items.py

# Test Django template rendering
"D:/code/Sales_App/virtual/Scripts/python.exe" tests/functional/template_test.py
```

**HTML Test Interfaces:**
- `tests/functional/final_chart_test.html` - Complete chart testing interface
- `tests/functional/test_chart.html` - Basic chart validation

### 🛠️ Utility Tests (`tests/utilities/`)
**Purpose:** Helper scripts for data management and system checks

**Available Utilities:**
```cmd
# Create test invoice data for development
"D:/code/Sales_App/virtual/Scripts/python.exe" tests/utilities/create_test_invoice.py

# Validate invoice data integrity
"D:/code/Sales_App/virtual/Scripts/python.exe" tests/utilities/check_invoices.py

# Check for null user references
"D:/code/Sales_App/virtual/Scripts/python.exe" tests/utilities/check_null_users.py
```

### ✅ Validation Tests (`tests/validation/`)
**Purpose:** Verify that fixes and implementations work correctly

**Available Validations:**
```cmd
# Validate all chart fixes and implementations
"D:/code/Sales_App/virtual/Scripts/python.exe" tests/validation/validate_chart_fixes.py

# Verify revenue calculation accuracy
"D:/code/Sales_App/virtual/Scripts/python.exe" tests/validation/verify_revenue_fix.py
```

**HTML Validation Interfaces:**
- `tests/validation/bulletproof_chart_test.html` - Chart bulletproofing validation
- `tests/validation/canvas_reuse_test.html` - Canvas reuse error testing

### 🐛 Debugging Tools (`tests/debugging/`)
**Purpose:** Development troubleshooting and diagnostic tools

**Available Debug Tools:**
```cmd
# Debug chart rendering issues
"D:/code/Sales_App/virtual/Scripts/python.exe" tests/debugging/debug_charts.py

# Debug revenue calculation problems
"D:/code/Sales_App/virtual/Scripts/python.exe" tests/debugging/revenue_summary_debug.py
```

**HTML Debug Interface:**
- `tests/debugging/chart_debug.html` - Interactive chart debugging

## 📋 Test Examples

### Example 1: Running a Utility Test
```cmd
D:\code\Sales_App\sales_management_project> "D:/code/Sales_App/virtual/Scripts/python.exe" tests/utilities/check_invoices.py

Output:
=== Invoice Data Analysis ===
Total invoices in database: 3
Invoice INV-20250802-001:
  - Total: $4200.00
  - Amount Paid: $4200.00
  - Payment Status: paid
  - Balance: $0.00
...
```

### Example 2: Using HTML Validation
1. Open in browser: `tests/validation/bulletproof_chart_test.html`
2. Watch console for chart initialization
3. Verify no canvas reuse errors
4. Check chart renders correctly

### Example 3: Functional Testing
```cmd
"D:/code/Sales_App/virtual/Scripts/python.exe" tests/functional/test_print_items.py

Output:
Invoices for 2025-08-02:
Total invoices: 2
Invoice: INV-20250802-001
Customer: Dylan
Items:
  - Item: 'Fetanyl' | Qty: 20 | Price: $200.00
...
```

## 🎯 Testing Workflows

### 1. **New Feature Development**
```cmd
# Step 1: Create test data
"D:/code/Sales_App/virtual/Scripts/python.exe" tests/utilities/create_test_invoice.py

# Step 2: Test the feature
"D:/code/Sales_App/virtual/Scripts/python.exe" tests/functional/test_[your_feature].py

# Step 3: Validate the implementation
"D:/code/Sales_App/virtual/Scripts/python.exe" tests/validation/validate_[feature].py
```

### 2. **Bug Investigation**
```cmd
# Step 1: Use debugging tools
"D:/code/Sales_App/virtual/Scripts/python.exe" tests/debugging/debug_[component].py

# Step 2: Check data integrity
"D:/code/Sales_App/virtual/Scripts/python.exe" tests/utilities/check_[data_type].py

# Step 3: Validate the fix
"D:/code/Sales_App/virtual/Scripts/python.exe" tests/validation/verify_[fix].py
```

### 3. **Chart/UI Testing**
```cmd
# Step 1: Run Python chart tests
"D:/code/Sales_App/virtual/Scripts/python.exe" tests/functional/test_django_chart.py

# Step 2: Open HTML validation in browser
file:///d:/code/Sales_App/sales_management_project/tests/validation/bulletproof_chart_test.html

# Step 3: Check for console errors and proper rendering
```

## 📊 Test Results Interpretation

### ✅ **Success Indicators:**
- No Python exceptions thrown
- All assertions pass
- HTML tests show "success" status
- Charts render without console errors
- Data integrity checks pass

### ❌ **Failure Indicators:**
- Python traceback errors
- Failed assertions
- HTML tests show "error" status
- Console errors in browser
- Data inconsistencies found

## 🔧 Creating New Tests

### For Python Tests:
```python
#!/usr/bin/env python
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sales_management_project.settings')
sys.path.append('d:\\code\\Sales_App\\sales_management_project')
django.setup()

# Your test code here
def test_feature():
    """Test description"""
    # Test implementation
    pass

if __name__ == "__main__":
    test_feature()
```

### For HTML Tests:
```html
<!DOCTYPE html>
<html>
<head>
    <title>Feature Test</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</head>
<body>
    <div id="test-container">
        <!-- Test UI elements -->
    </div>
    <script>
        // Test implementation
    </script>
</body>
</html>
```

## 🎯 Best Practices

1. **Always activate virtual environment first**
2. **Use full Python path for consistent execution**
3. **Check both Python output and browser console for HTML tests**
4. **Run utility tests before functional tests to ensure clean data**
5. **Use validation tests after making changes to verify fixes**
6. **Keep test data separate from production data**

## 📞 Troubleshooting

### Common Issues:
- **Django not found:** Ensure virtual environment is activated
- **Module import errors:** Check Python path configuration
- **Database errors:** Verify Django settings and database connectivity
- **Chart not rendering:** Check browser console for JavaScript errors

### Debug Steps:
1. Run utility tests to check data integrity
2. Use debugging tools to isolate issues
3. Check HTML validation tests for UI components
4. Verify all dependencies are installed

---

*This testing system provides comprehensive coverage for your Django Sales Management application with organized, categorized tests for efficient development and debugging.*
