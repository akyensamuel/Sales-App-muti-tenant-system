# 📚 Documentation Index

## 📁 Directory Structure

```
docs/
├── features/           # Feature guides and documentation
│   ├── PRINT_FUNCTIONALITY_GUIDE.md
│   └── SEARCH_FUNCTIONALITY_GUIDE.md
├── fixes/             # Bug fixes and improvements
│   ├── ACTION_BUTTON_IMPROVEMENTS.md
│   ├── CANVAS_REUSE_FIX.md
│   ├── CHART_FIX_SUMMARY.md
│   ├── CHART_IMPLEMENTATION_COMPLETE.md
│   └── DARK_MODE_FIXES_COMPLETE.md
tests/
├── debugging/         # Debugging scripts and tools
│   ├── debug_charts.py
│   └── revenue_summary_debug.py
├── functional/        # Functional tests
│   ├── template_test.py
│   ├── test_django_chart.py
│   └── test_print_items.py
├── utilities/         # Test utilities and helpers
│   ├── check_invoices.py
│   ├── check_null_users.py
│   └── create_test_invoice.py
└── validation/        # Validation scripts
    ├── validate_chart_fixes.py
    └── verify_revenue_fix.py
```

## 📖 Documentation Overview

### 🚀 Features
- **[Print Functionality Guide](features/PRINT_FUNCTIONALITY_GUIDE.md)** - Complete guide for print features across the application
- **[Search Functionality Guide](features/SEARCH_FUNCTIONALITY_GUIDE.md)** - Documentation for search and filtering capabilities

### 🔧 Fixes & Improvements
- **[Action Button Improvements](fixes/ACTION_BUTTON_IMPROVEMENTS.md)** - Enhanced button sizing and usability improvements
- **[Canvas Reuse Fix](fixes/CANVAS_REUSE_FIX.md)** - Resolution for Chart.js canvas reuse errors
- **[Chart Fix Summary](fixes/CHART_FIX_SUMMARY.md)** - Overview of chart-related fixes
- **[Chart Implementation Complete](fixes/CHART_IMPLEMENTATION_COMPLETE.md)** - Comprehensive chart implementation documentation
- **[Dark Mode Fixes Complete](fixes/DARK_MODE_FIXES_COMPLETE.md)** - Complete dark mode support implementation

## 🧪 Testing Overview

### 🔍 Functional Tests
- **template_test.py** - Template rendering and functionality tests
- **test_django_chart.py** - Chart functionality and rendering tests
- **test_print_items.py** - Print functionality validation tests

### 🐛 Debugging Tools
- **debug_charts.py** - Chart debugging and troubleshooting utility
- **revenue_summary_debug.py** - Revenue calculation debugging tool

### 🛠️ Utilities
- **check_invoices.py** - Invoice data validation utility
- **check_null_users.py** - User data integrity checker
- **create_test_invoice.py** - Test invoice generation utility

### ✅ Validation Scripts
- **validate_chart_fixes.py** - Comprehensive chart fix validation
- **verify_revenue_fix.py** - Revenue calculation verification

## 📋 Usage Guidelines

### Running Tests
```bash
# Functional tests
python tests/functional/test_django_chart.py
python tests/functional/test_print_items.py

# Validation scripts
python tests/validation/validate_chart_fixes.py
python tests/validation/verify_revenue_fix.py

# Debugging tools
python tests/debugging/debug_charts.py
python tests/debugging/revenue_summary_debug.py

# Utilities
python tests/utilities/create_test_invoice.py
python tests/utilities/check_invoices.py
```

### Documentation Updates
- Add new feature documentation to `docs/features/`
- Add fix documentation to `docs/fixes/`
- Update this index when adding new documentation

### Test Organization
- **Functional tests**: End-to-end feature testing
- **Debugging**: Development and troubleshooting tools
- **Utilities**: Helper scripts for testing and data management
- **Validation**: Scripts to verify fixes and implementations

---
*Last updated: August 2, 2025*
