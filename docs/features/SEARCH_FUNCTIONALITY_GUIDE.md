# Enhanced Search Functionality - Manager Dashboard

## Overview
The manager dashboard now includes a comprehensive search functionality that allows searching by multiple parameters with "OR" logic.

## Search Parameters

### 1. Date Range Search
- **Start Date**: Find invoices from this date onwards
- **End Date**: Find invoices up to this date
- **Combined**: Find invoices within the date range

### 2. Customer Name Search
- **Type**: Text input with case-insensitive partial matching
- **Example**: Searching "john" will find "John Doe", "Johnny Smith", etc.

### 3. Invoice Number Search
- **Type**: Text input with case-insensitive partial matching
- **Example**: Searching "INV" will find "INV-001", "INV-002", etc.

## Search Logic

### OR Search Behavior
The search uses **OR logic**, meaning invoices will be returned if they match **ANY** of the provided criteria:

- Invoice matches date range **OR**
- Customer name contains search term **OR** 
- Invoice number contains search term

### Examples

#### Example 1: Multiple Criteria
- Start Date: 2025-01-01
- Customer Name: "smith"
- Invoice Number: "INV-100"

**Result**: Returns all invoices that:
- Are from 2025-01-01 onwards, OR
- Have "smith" in customer name, OR  
- Have "INV-100" in invoice number

#### Example 2: Single Criteria
- Customer Name: "john"

**Result**: Returns all invoices with "john" in the customer name

## Default Behavior

### No Search Parameters
When no search parameters are provided, the dashboard shows:
- **Today's invoices only**

### Clear & Show Today Button
- Clears all search filters
- Returns to default view (today's invoices)

## User Interface Features

### Visual Feedback
- **Active Search Indicators**: Blue highlighting on inputs with values
- **Search Results Summary**: Shows what was searched and result count
- **Empty State Messages**: Different messages for no results vs. no today's invoices

### Keyboard Shortcuts
- **Enter Key**: Submit search from any input field
- **Real-time Validation**: Visual feedback as you type

### Search Results Display
- **Result Count**: Shows number of invoices found
- **Search Terms**: Displays active search criteria as tags
- **Total Sales**: Calculates total for filtered results

## Technical Implementation

### Backend (views.py)
```python
# OR search using Django Q objects
from django.db.models import Q
search_conditions = Q()

if start_date and end_date:
    search_conditions |= Q(date_of_sale__gte=start_date, date_of_sale__lte=end_date)
elif start_date:
    search_conditions |= Q(date_of_sale__gte=start_date)
elif end_date:
    search_conditions |= Q(date_of_sale__lte=end_date)

if customer_name:
    search_conditions |= Q(customer_name__icontains=customer_name)

if invoice_no:
    search_conditions |= Q(invoice_no__icontains=invoice_no)

invoices = invoices.filter(search_conditions)
```

### Frontend Features
- Responsive grid layout for search inputs
- Modern Tailwind CSS styling
- JavaScript enhancements for better UX
- Form validation and feedback

## Usage Tips

1. **Quick Customer Search**: Just type part of the customer's name
2. **Invoice Lookup**: Enter partial invoice numbers for quick finding
3. **Date Ranges**: Use both start and end dates for specific periods
4. **Combine Searches**: Use multiple criteria to cast a wider net
5. **Clear Filters**: Use "Clear & Show Today" to reset to default view

## Security
- All search parameters are properly sanitized
- Uses Django ORM to prevent SQL injection
- Maintains existing permission controls (Manager/Admin only)
