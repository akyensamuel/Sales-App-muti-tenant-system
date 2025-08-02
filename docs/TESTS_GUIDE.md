# 🧪 Sales Management Project - Testing Guide

## Overview

This comprehensive testing guide covers all testing strategies, tools, and procedures for the Sales Management Project. It includes testing for features, fixes, and ongoing development.

## 📁 Project Structure

```
sales_management_project/
├── docs/
│   ├── features/           # Feature documentation
│   ├── fixes/             # Bug fix documentation
│   └── TESTS_GUIDE.md     # This file
├── tests/
│   ├── debug/             # Development & debugging scripts
│   ├── html/              # Frontend test files
│   ├── integration/       # Integration tests
│   ├── utils/             # Test utilities & helpers
│   └── README.md          # Test structure documentation
├── sales_app/tests.py     # Sales app unit tests
├── accounting_app/tests.py # Accounting app unit tests
├── core/tests.py          # Core app unit tests
└── run_tests.py           # Central test runner
```

## 🧪 Testing Categories

### 1. Unit Tests
**Location**: Individual app `tests.py` files
**Purpose**: Test individual functions, models, and views in isolation

**Running Unit Tests:**
```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test sales_app
python manage.py test accounting_app
python manage.py test core

# Run with coverage
python -m coverage run --source='.' manage.py test
python -m coverage report
```

### 2. Integration Tests
**Location**: `tests/integration/`
**Purpose**: Test interactions between different components

**Available Integration Tests:**
- `test_django_chart.py` - Chart.js integration testing
- `template_test.py` - Template rendering and context testing

**Running Integration Tests:**
```bash
python run_tests.py integration
# Or manually:
python tests/integration/test_django_chart.py
python tests/integration/template_test.py
```

### 3. Debug Scripts
**Location**: `tests/debug/`
**Purpose**: Development debugging and issue investigation

**Available Debug Scripts:**
- `debug_charts.py` - Chart functionality debugging
- `revenue_summary_debug.py` - Revenue calculation verification
- `test_print_items.py` - Print functionality testing
- `validate_chart_fixes.py` - Chart fix validation
- `verify_revenue_fix.py` - Revenue fix verification

**Running Debug Scripts:**
```bash
python run_tests.py debug  # Lists available scripts
python tests/debug/debug_charts.py
python tests/debug/revenue_summary_debug.py
```

### 4. Utility Scripts
**Location**: `tests/utils/`
**Purpose**: Data validation and test data creation

**Available Utilities:**
- `create_test_invoice.py` - Generate test invoices
- `check_invoices.py` - Validate invoice data integrity
- `check_null_users.py` - Check for data consistency issues

**Running Utilities:**
```bash
python run_tests.py utils  # Lists available utilities
python tests/utils/create_test_invoice.py
python tests/utils/check_invoices.py
```

### 5. Frontend Tests
**Location**: `tests/html/`
**Purpose**: HTML/JavaScript functionality testing

**Available HTML Tests:**
- `bulletproof_chart_test.html` - Chart.js implementation testing
- `canvas_reuse_test.html` - Canvas element reuse testing
- `chart_debug.html` - Chart debugging interface
- `final_chart_test.html` - Final chart implementation
- `test_chart.html` - Basic chart testing

**Running HTML Tests:**
```bash
# Open in browser for manual testing
start tests/html/bulletproof_chart_test.html
start tests/html/chart_debug.html
```

## 🎯 Feature-Specific Testing

### Print Functionality Testing
**Reference**: `docs/features/PRINT_FUNCTIONALITY_GUIDE.md`

**Test Scenarios:**
1. **Print Today's Invoices**
   ```bash
   # Debug print functionality
   python tests/debug/test_print_items.py
   ```
   - Verify today's invoices are correctly fetched
   - Test print layout and formatting
   - Validate summary statistics

2. **Print Search Results**
   - Test with various search criteria
   - Verify filtered results are correctly displayed
   - Test empty search results handling

3. **Print Specific Date**
   - Test with dates containing data
   - Test with dates containing no data
   - Verify date range calculations

**Manual Testing Checklist:**
- [ ] Print preview displays correctly
- [ ] All invoice data is present
- [ ] Summary statistics are accurate
- [ ] Page breaks work properly
- [ ] Print styling is applied correctly

### Search Functionality Testing
**Reference**: `docs/features/SEARCH_FUNCTIONALITY_GUIDE.md`

**Test Scenarios:**
1. **OR Logic Search**
   ```python
   # Test search logic in Django shell
   python manage.py shell
   from sales_app.models import Invoice
   
   # Test OR search behavior
   invoices = Invoice.objects.filter(
       customer_name__icontains='test'
   ) | Invoice.objects.filter(
       invoice_no__icontains='INV'
   )
   ```

2. **Date Range Search**
   - Test single date searches
   - Test date range searches
   - Test edge cases (future dates, invalid ranges)

3. **Partial Matching**
   - Test case-insensitive search
   - Test partial string matching
   - Test special characters

**Manual Testing Checklist:**
- [ ] Search returns correct results for each parameter
- [ ] OR logic works correctly with multiple parameters
- [ ] Case-insensitive search works
- [ ] Date range filtering works correctly
- [ ] Search results display properly

### Chart Functionality Testing
**Reference**: `docs/fixes/CHART_*.md` files

**Test Scenarios:**
1. **Canvas Reuse Prevention**
   ```bash
   # Test chart functionality
   python tests/debug/debug_charts.py
   python tests/debug/validate_chart_fixes.py
   ```

2. **Chart.js Loading**
   ```html
   <!-- Test in: tests/html/bulletproof_chart_test.html -->
   <!-- Verify Chart.js loads correctly -->
   ```

3. **Data Processing**
   ```bash
   # Test revenue calculations
   python tests/debug/revenue_summary_debug.py
   python tests/debug/verify_revenue_fix.py
   ```

**Manual Testing Checklist:**
- [ ] Charts load without errors
- [ ] No canvas reuse errors in console
- [ ] Data displays correctly
- [ ] Charts are responsive
- [ ] Dark mode compatibility

### Action Button Testing
**Reference**: `docs/features/ACTION_BUTTON_IMPROVEMENTS.md`

**Test Scenarios:**
1. **Button Sizing**
   - Verify buttons meet minimum touch target size (44px)
   - Test on different screen sizes
   - Verify accessibility compliance

2. **Hover States**
   - Test hover animations
   - Verify transition effects
   - Test in both light and dark modes

**Manual Testing Checklist:**
- [ ] Buttons are appropriately sized
- [ ] Hover effects work correctly
- [ ] Touch targets are accessible
- [ ] Icons and text are properly aligned
- [ ] Dark mode styling works

### Dark Mode Testing
**Reference**: `docs/fixes/DARK_MODE_FIXES_COMPLETE.md`

**Test Scenarios:**
1. **Theme Switching**
   - Test automatic dark mode detection
   - Test manual theme toggle
   - Verify persistence across sessions

2. **Component Coverage**
   - Test all UI components in dark mode
   - Verify text contrast ratios
   - Test form elements and buttons

**Manual Testing Checklist:**
- [ ] All text is readable in dark mode
- [ ] Color contrasts meet accessibility standards
- [ ] Interactive elements work in both modes
- [ ] Charts adapt to dark theme
- [ ] No visual artifacts or broken styling

## 🔄 Continuous Testing Workflow

### Pre-Commit Testing
```bash
# Run before committing changes
python run_tests.py all
python tests/utils/check_invoices.py
python tests/utils/check_null_users.py
```

### Post-Feature Development
```bash
# After implementing a new feature
python manage.py test
python tests/integration/test_django_chart.py
# Manual testing of the specific feature
```

### Pre-Deployment Testing
```bash
# Before deploying to production
python manage.py test
python manage.py collectstatic --noinput
python tests/debug/debug_charts.py
python tests/debug/revenue_summary_debug.py
# Full manual testing of critical features
```

## 🐛 Debugging and Troubleshooting

### Common Issues and Solutions

1. **Chart Not Displaying**
   ```bash
   # Debug chart issues
   python tests/debug/debug_charts.py
   # Check console for JavaScript errors
   # Verify Chart.js is loading
   ```

2. **Print Issues**
   ```bash
   # Debug print functionality
   python tests/debug/test_print_items.py
   # Check CSS print styles
   # Verify data is being fetched correctly
   ```

3. **Search Not Working**
   ```bash
   # Debug search functionality
   python tests/utils/check_invoices.py
   # Check database queries
   # Verify search parameters
   ```

4. **Dark Mode Issues**
   - Check CSS class conflicts
   - Verify Tailwind dark mode classes
   - Test in different browsers

### Debug Data Generation
```bash
# Create test data for debugging
python tests/utils/create_test_invoice.py

# Verify data integrity
python tests/utils/check_invoices.py
python tests/utils/check_null_users.py
```

## 📊 Test Coverage

### Current Coverage Areas
- ✅ Model validation and business logic
- ✅ View rendering and context data
- ✅ Form validation and processing
- ✅ Chart functionality and data processing
- ✅ Print functionality
- ✅ Search and filtering
- ✅ Dark mode compatibility
- ✅ Action button usability

### Areas for Improvement
- [ ] Automated UI testing with Selenium
- [ ] API endpoint testing
- [ ] Performance testing
- [ ] Mobile responsiveness testing
- [ ] Cross-browser compatibility testing

## 🚀 Getting Started with Testing

### For New Developers
1. **Set up test environment:**
   ```bash
   # Install dependencies
   pip install -r requirements.txt
   
   # Run initial tests
   python run_tests.py all
   ```

2. **Create test data:**
   ```bash
   python tests/utils/create_test_invoice.py
   ```

3. **Run debug scripts to understand the system:**
   ```bash
   python tests/debug/debug_charts.py
   python tests/debug/revenue_summary_debug.py
   ```

### Writing New Tests
1. **Unit tests**: Add to appropriate app's `tests.py` file
2. **Integration tests**: Add to `tests/integration/`
3. **Debug scripts**: Add to `tests/debug/`
4. **Utilities**: Add to `tests/utils/`
5. **HTML tests**: Add to `tests/html/`

### Test File Template
```python
#!/usr/bin/env python
import os
import sys
from pathlib import Path

# Add tests directory to path and setup Django
sys.path.insert(0, str(Path(__file__).parent.parent))
from django_setup import setup_django
setup_django()

# Your test code here
from sales_app.models import Invoice

def test_feature():
    """Test description"""
    # Test implementation
    pass

if __name__ == "__main__":
    test_feature()
```

## 📞 Support

- **Test Structure**: See `tests/README.md`
- **Feature Documentation**: See `docs/features/`
- **Fix Documentation**: See `docs/fixes/`
- **Debug Scripts**: Use `python run_tests.py debug`
- **Utilities**: Use `python run_tests.py utils`

This testing guide ensures comprehensive coverage of all Sales Management Project features and provides clear procedures for maintaining code quality and reliability.
