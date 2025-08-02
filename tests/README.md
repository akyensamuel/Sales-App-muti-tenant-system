# 🧪 Tests Di### 🔧 `/debugging/` - Debug Tools
Development tools for troubleshooting and diagnosing issues.

- **`debug_charts.py`** - Chart debugging and troubleshooting utility
- **`revenue_summary_debug.py`** - Revenue calculation debugging tool
- **`chart_debug.html`** - HTML chart debugging interface

### 🛠️ `/utilities/` - Test Utilities
Helper scripts for test data management and system checks.

- **`check_invoices.py`** - Invoice data validation and integrity checks
- **`check_null_users.py`** - User data integrity checker
- **`template_test_output.js`** - Template output testing utility

### ✅ `/validation/` - Validation Scripts
Scripts to verify that fixes and implementations are working correctly.

- **`validate_chart_fixes.py`** - Comprehensive chart fix validation
- **`verify_revenue_fix.py`** - Revenue calculation verification
- **`bulletproof_chart_test.html`** - Chart bulletproofing validation
- **`canvas_reuse_test.html`** - Canvas reuse error testingrectory contains all testing scripts, debugging tools, utilities, and validation scripts for the Sales Management System.

## 📁 Directory Structure

### 🔍 `/functional/` - Functional Tests
End-to-end tests that validate complete features and user workflows.

- **`test_django_chart.py`** - Tests Chart.js implementation and rendering
- **`test_print_items.py`** - Tests print functionality with item names
- **`template_test.py`** - Tests template rendering and functionality
- **`final_chart_test.html`** - Final chart implementation testing interface
- **`test_chart.html`** - Chart testing and validation interface

### 🐛 `/debugging/` - Debugging Tools
Development tools for troubleshooting and diagnosing issues.

- **`debug_charts.py`** - Chart debugging and troubleshooting utility
- **`revenue_summary_debug.py`** - Revenue calculation debugging tool

### 🛠️ `/utilities/` - Test Utilities
Helper scripts for test data management and system checks.

- **`check_invoices.py`** - Invoice data validation and integrity checks
- **`check_null_users.py`** - User data integrity checker
- **`create_test_invoice.py`** - Generate test invoices for development

### ✅ `/validation/` - Validation Scripts
Scripts to verify that fixes and implementations are working correctly.

- **`validate_chart_fixes.py`** - Comprehensive chart fix validation
- **`verify_revenue_fix.py`** - Revenue calculation verification

## 🚀 Running Tests

### Prerequisites
Make sure your Django environment is properly configured:

```bash
# Activate virtual environment
D:/code/Sales_App/virtual/Scripts/activate

# Set Django settings
set DJANGO_SETTINGS_MODULE=sales_management_project.settings
```

### Functional Tests
```bash
# Test chart functionality
python tests/functional/test_django_chart.py

# Test print features
python tests/functional/test_print_items.py

# Test template rendering
python tests/functional/template_test.py
```

### Validation Scripts
```bash
# Validate chart implementations
python tests/validation/validate_chart_fixes.py

# Verify revenue calculations
python tests/validation/verify_revenue_fix.py
```

### Debugging Tools
```bash
# Debug chart issues
python tests/debugging/debug_charts.py

# Debug revenue calculations
python tests/debugging/revenue_summary_debug.py
```

### Utilities
```bash
# Create test data
python tests/utilities/create_test_invoice.py

# Check data integrity
python tests/utilities/check_invoices.py
python tests/utilities/check_null_users.py
```

## 📋 Best Practices

### Adding New Tests
1. **Functional tests**: Add to `/functional/` for end-to-end feature testing
2. **Debugging tools**: Add to `/debugging/` for development troubleshooting
3. **Utilities**: Add to `/utilities/` for helper scripts and data management
4. **Validation**: Add to `/validation/` for verifying fixes and implementations

### Test Naming Convention
- Use descriptive names: `test_[feature]_[functionality].py`
- Use action verbs for utilities: `create_`, `check_`, `validate_`, `verify_`
- Use debug prefix for debugging tools: `debug_[component].py`

### Documentation
- Include docstrings in all test functions
- Add comments for complex test logic
- Update this README when adding new test categories

## 🔧 Test Environment Setup

### Django Test Client
Most tests use Django's test client for authentication and HTTP requests:

```python
from django.test import Client
from django.contrib.auth.models import User

client = Client()
user = User.objects.first()
client.force_login(user)
```

### Chart Testing
Chart tests verify Chart.js implementation and canvas management:

```python
# Check for Chart.js elements
checks = [
    ('Chart.js script', 'chart.js' in content.lower()),
    ('Canvas element', 'chartId' in content),
    ('Chart constructor', 'new Chart(' in content),
]
```

### Print Testing
Print tests validate item visibility and formatting:

```python
# Verify print content
print_content = response.content.decode('utf-8')
assert 'item_name' in print_content
```

## 📊 Test Coverage Areas

- ✅ Chart.js implementation and canvas management
- ✅ Print functionality with proper item display
- ✅ Template rendering and context data
- ✅ Revenue calculation accuracy
- ✅ Invoice data integrity
- ✅ User authentication and permissions
- ✅ Dark mode compatibility
- ✅ Responsive design elements

---
*For more information, see the main documentation in `/docs/README.md`*
