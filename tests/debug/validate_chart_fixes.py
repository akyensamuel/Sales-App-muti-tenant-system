#!/usr/bin/env python3
"""
Validate that chart fixes have been properly applied to both 
revenue tracking and profit & loss report templates.
"""

def check_file_content(file_path, checks, description):
    """Check if a file contains expected content patterns."""
    print(f"\n📊 Checking {description}:")
    print(f"   File: {file_path}")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        results = []
        for check_name, pattern in checks:
            found = pattern in content
            status = "✅" if found else "❌"
            print(f"  {status} {check_name}: {'Found' if found else 'Not found'}")
            results.append(found)
        
        success_rate = sum(results) / len(results) * 100
        print(f"  📈 Success rate: {success_rate:.1f}% ({sum(results)}/{len(results)})")
        
        return success_rate > 80  # Consider success if 80%+ checks pass
        
    except FileNotFoundError:
        print(f"  ❌ File not found: {file_path}")
        return False
    except Exception as e:
        print(f"  ❌ Error reading file: {e}")
        return False

def main():
    print("🔍 VALIDATING CHART FIXES")
    print("=" * 50)
    
    # Revenue tracking template checks
    revenue_checks = [
        ("Chart.js CDN loading", "cdn.jsdelivr.net/npm/chart.js"),
        ("Canvas element with ID", 'id="revenueChart"'),
        ("DOM ready listener", "DOMContentLoaded"),
        ("Global chart instance", "revenueChartInstance"),
        ("Chart registry cleanup", "Chart.getChart("),
        ("Chart destruction", ".destroy()"),
        ("New Chart constructor", "new Chart("),
        ("Monthly data usage", "monthly_data"),
        ("Loading status display", "Loading chart..."),
        ("Error handling", "Error loading chart"),
    ]
    
    revenue_file = "accounting_app/templates/accounting_app/revenue_tracking.html"
    revenue_success = check_file_content(revenue_file, revenue_checks, "Revenue Tracking Chart")
    
    # Profit & loss template checks  
    expense_checks = [
        ("Chart.js CDN loading", "cdn.jsdelivr.net/npm/chart.js"),
        ("Canvas element with ID", 'id="expenseChart"'),
        ("DOM ready listener", "DOMContentLoaded"),
        ("Global chart instance", "expenseChartInstance"),
        ("Chart registry cleanup", "Chart.getChart("),
        ("Chart destruction", ".destroy()"),
        ("New Chart constructor", "new Chart("),
        ("Expense data usage", "expense_data"),
        ("Doughnut chart type", "type: 'doughnut'"),
        ("Loading status display", "Loading chart..."),
    ]
    
    expense_file = "accounting_app/templates/accounting_app/profit_loss_report.html"
    expense_success = check_file_content(expense_file, expense_checks, "Expense Distribution Chart")
    
    # Base template check
    base_checks = [
        ("Extra JS block", "{% block extra_js %}"),
        ("Block end tag", "{% endblock %}"),
    ]
    
    base_file = "core/templates/core/base.html"
    base_success = check_file_content(base_file, base_checks, "Base Template JS Support")
    
    # Overall results
    print(f"\n📊 OVERALL VALIDATION RESULTS")
    print("=" * 50)
    
    results = [
        ("Revenue Chart Template", revenue_success),
        ("Expense Chart Template", expense_success),
        ("Base Template Support", base_success),
    ]
    
    for check_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status} {check_name}")
    
    total_success = sum(r[1] for r in results)
    print(f"\n🎯 Total: {total_success}/{len(results)} components validated successfully")
    
    if total_success == len(results):
        print("🎉 ALL CHART FIXES VALIDATED SUCCESSFULLY!")
        print("   Both revenue and expense charts should now display without canvas reuse errors.")
    else:
        print("⚠️  Some issues detected - review the failed checks above.")

if __name__ == "__main__":
    main()
