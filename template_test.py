#!/usr/bin/env python
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sales_management_project.settings')
sys.path.append('d:\\code\\Sales_App\\sales_management_project')
django.setup()

from django.template import Template, Context
from sales_app.models import Invoice
from django.utils import timezone
from django.db.models import Sum
from datetime import timedelta

print("=== Testing Chart Template Rendering Directly ===")
print()

# Get the same data that the view would provide
end_date = timezone.now().date()
start_date = end_date - timedelta(days=365)

monthly_data = []
for i in range(12):
    month_start = (start_date.replace(day=1) + timedelta(days=32*i)).replace(day=1)
    month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
    
    if month_end > end_date:
        month_end = end_date
    
    revenue = Invoice.objects.filter(
        date_of_sale__range=[month_start, month_end]
    ).aggregate(total=Sum('total'))['total'] or 0
    
    monthly_data.append({
        'month': month_start.strftime('%B %Y'),
        'revenue': float(revenue),
        'month_start': month_start,
        'month_end': month_end
    })

total_12_month_revenue = sum(month['revenue'] for month in monthly_data)

print(f"📊 Found {len(monthly_data)} months of data")
print(f"💰 Total revenue: ${total_12_month_revenue:,.2f}")

# Test the JavaScript template generation
chart_js_template = """
<script>
    document.addEventListener('DOMContentLoaded', function() {
        const chartLabels = [
            {% for month in monthly_data %}
                '{{ month.month }}'{% if not forloop.last %},{% endif %}
            {% endfor %}
        ];
        
        const chartData = [
            {% for month in monthly_data %}
                {{ month.revenue }}{% if not forloop.last %},{% endif %}
            {% endfor %}
        ];
        
        console.log('Chart labels:', chartLabels);
        console.log('Chart data:', chartData);
        
        const revenueChart = new Chart(document.getElementById('revenueChart').getContext('2d'), {
            type: 'line',
            data: {
                labels: chartLabels,
                datasets: [{
                    label: 'Monthly Revenue',
                    data: chartData,
                    borderColor: '#3B82F6',
                    backgroundColor: 'rgba(59, 130, 246, 0.1)',
                    fill: true,
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: { beginAtZero: true }
                }
            }
        });
    });
</script>
"""

template = Template(chart_js_template)
context = Context({'monthly_data': monthly_data})
rendered_js = template.render(context)

print("\n✅ Template rendered successfully!")
print("\n📄 Rendered JavaScript:")
print("=" * 50)
print(rendered_js)
print("=" * 50)

# Check for key elements
if 'July 2025' in rendered_js:
    print("✅ July 2025 found in rendered JavaScript")
else:
    print("❌ July 2025 NOT found in rendered JavaScript")

if '20371' in rendered_js:
    print("✅ Revenue value 20371 found in rendered JavaScript")
else:
    print("❌ Revenue value 20371 NOT found in rendered JavaScript")

if 'chartLabels' in rendered_js and 'chartData' in rendered_js:
    print("✅ Chart variables properly defined")
else:
    print("❌ Chart variables NOT properly defined")

# Save to file for inspection
with open('template_test_output.js', 'w') as f:
    f.write(rendered_js)

print(f"\n📁 Full rendered JavaScript saved to 'template_test_output.js'")
