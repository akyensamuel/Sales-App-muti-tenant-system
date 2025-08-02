# Test Structure for Sales Management Project

This directory contains all testing and development utilities for the Sales Management Project.

## Directory Structure

```
tests/
├── __init__.py
├── debug/              # Development and debugging scripts
│   ├── __init__.py
│   ├── debug_charts.py
│   ├── revenue_summary_debug.py
│   ├── template_test_output.js
│   ├── test_print_items.py
│   ├── validate_chart_fixes.py
│   └── verify_revenue_fix.py
├── html/               # HTML test files for frontend testing
│   ├── bulletproof_chart_test.html
│   ├── canvas_reuse_test.html
│   ├── chart_debug.html
│   ├── final_chart_test.html
│   └── test_chart.html
├── integration/        # Integration tests
│   ├── __init__.py
│   ├── template_test.py
│   └── test_django_chart.py
└── utils/             # Test utilities and helpers
    ├── __init__.py
    ├── check_invoices.py
    ├── check_null_users.py
    └── create_test_invoice.py
```

## Usage

### Running Integration Tests
```bash
# Run all Django tests
python manage.py test

# Run specific app tests
python manage.py test sales_app
python manage.py test accounting_app
python manage.py test core

# Run integration tests
python tests/integration/test_django_chart.py
python tests/integration/template_test.py
```

### Debug Scripts
```bash
# Debug chart functionality
python tests/debug/debug_charts.py

# Check revenue calculations
python tests/debug/revenue_summary_debug.py

# Validate chart fixes
python tests/debug/validate_chart_fixes.py

# Print items for debugging
python tests/debug/test_print_items.py
```

### Utility Scripts
```bash
# Create test data
python tests/utils/create_test_invoice.py

# Check data integrity
python tests/utils/check_invoices.py
python tests/utils/check_null_users.py
```

### HTML Tests
Open the HTML files in `tests/html/` directory in a web browser to test frontend functionality:
- `bulletproof_chart_test.html` - Chart.js implementation testing
- `canvas_reuse_test.html` - Canvas element reuse testing
- `chart_debug.html` - Chart debugging interface
- `final_chart_test.html` - Final chart implementation
- `test_chart.html` - Basic chart testing

## Test Data Management

Each app has its own `tests.py` file for unit tests:
- `sales_app/tests.py` - Sales functionality tests
- `accounting_app/tests.py` - Accounting functionality tests  
- `core/tests.py` - Core functionality tests

## Best Practices

1. **Unit Tests**: Keep in individual app `tests.py` files
2. **Integration Tests**: Place in `tests/integration/`
3. **Debug Scripts**: Place in `tests/debug/`
4. **Test Utilities**: Place in `tests/utils/`
5. **HTML Tests**: Place in `tests/html/`

## Contributing

When adding new test files:
1. Choose the appropriate directory based on test type
2. Follow the naming convention: `test_*.py` for Python tests
3. Add proper documentation and comments
4. Update this README if adding new categories
