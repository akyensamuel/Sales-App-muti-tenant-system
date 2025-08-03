# Sales Management System

A comprehensive Django-based multi-tenant sales management system with complete data isolation, advanced sales tracking, and integrated accounting features. Built for businesses requiring secure multi-organization support.

## 🚀 Key Features

### 🏢 **Multi-Tenancy & Organization Management**
- **Complete Data Isolation**: Separate PostgreSQL databases per tenant
- **Subdomain-Based Access**: `tenant.domain.com` routing with middleware
- **Supabase Integration**: Main database for tenant configurations
- **Production-Ready**: Supports unlimited tenants with independent scaling

### 🔐 **User Management & Security**
- **Role-Based Access Control**:
  - **Admin**: Full system access, user management, settings
  - **Managers**: Sales oversight, reporting, invoice management
  - **Cashiers**: Sales entry, basic operations
- **Secure Authentication**: Django built-in with custom middleware
- **Group-Based Permissions**: Dynamic navigation and feature access

### 📊 **Sales Management**
- **Advanced Sales Entry**:
  - Multi-item invoice creation with AJAX
  - Real-time stock validation and price calculation
  - Customer management with contact tracking
  - Automatic inventory updates
  - Local storage auto-save for data protection

- **Smart Product Management**:
  - Autocomplete product search
  - Live stock level display
  - Bulk product operations
  - Category-based organization

### 📋 **Invoice & Receipt System**
- **Professional Invoicing**:
  - Auto-generated invoice numbers
  - Detailed line items with calculations
  - Payment tracking (paid/unpaid/partial)
  - Invoice editing and cancellation
  - Stock restoration on cancellation

- **Print System**:
  - Thermal receipt printing
  - A4 invoice templates
  - Auto-print on sale completion
  - Print-optimized layouts

### 💰 **Accounting & Financial Management**
- **Comprehensive Financial Dashboard:**
  - Monthly revenue and expense tracking
  - Real-time profit & loss calculations
  - Outstanding invoice monitoring
  - Financial KPI cards with visual indicators
  - Quick access to all accounting functions

- **Expense Management:**
  - Detailed expense tracking with categories
  - Receipt file upload and storage
  - Vendor and payment method tracking
  - Recurring expense marking
  - Advanced filtering and search capabilities
  - Bulk expense operations

- **Financial Reporting:**
  - **Profit & Loss Reports:** Monthly and annual P&L statements
  - **Revenue Analysis:** 12-month revenue trends with charts
  - **Expense Breakdown:** Category-wise expense analysis
  - **Outstanding Invoices:** Payment status tracking and aging reports
  - **Tax Preparation:** Automated tax calculations and reporting

- **Audit Trail & Compliance:**
  - Complete audit log of all financial activities
  - User action tracking with timestamps
  - IP address logging for security
  - Comprehensive change history
  - Export capabilities for external auditing

### 📊 **Advanced Search & Filtering**
- **Multi-Parameter Search:**
  - Customer name search (partial matching)
  - Invoice number search
  - Date range filtering
  - OR-based search logic for flexible results
- **Real-time Search Results:**
  - Live filtering with visual feedback
  - Search criteria persistence
  - Results summary with statistics

### 📈 **Manager Dashboard**
- **Professional Interface:**
  - Modern card-based layout with gradient backgrounds
  - Sales summary cards (Total Sales, Invoice Count, Averages)
  - Real-time statistics and KPI tracking
  - Responsive design for all screen sizes

- **Comprehensive Reporting:**
  - Daily sales reports
  - Search result exports
  - Professional print layouts for business documentation
  - Date-specific report generation

### 🖨️ **Advanced Print Functionality**
- **Multiple Print Options:**
  - **Print Today:** Current day's invoices in professional format
  - **Print Search Results:** Export filtered results to print
  - **Print Specific Date:** Historical date report generation
  - **Individual Receipts:** Thermal printer-optimized receipts

- **Professional Report Format:**
  - Company header and branding
  - Detailed invoice breakdowns with items
  - Summary statistics and totals
  - Print-optimized A4 layouts
  - Auto-generated timestamps and user attribution

### 📦 **Inventory Management**
- **Real-Time Stock Tracking:**
  - Automatic stock deduction on sales
  - Stock restoration on invoice deletion
  - Low stock warnings during sales entry
  - Inventory level validation

- **Product Management (Admin):**
  - Add, edit, delete products
  - Price management
  - Stock level tracking
  - Product search and organization

### 💾 **Data Management**
- **Auto-Save Technology:**
  - Local storage backup during form entry
  - Form restoration on page reload
  - Data persistence across sessions
  - Loss prevention mechanisms

- **Audit Trail:**
  - Administrative action logging
  - User activity tracking
  - Stock movement history
  - Invoice modification logs

## 🎨 **User Interface Features**

### 🌓 **Modern Design**
- **Tailwind CSS Framework:** Clean, responsive, professional design
- **Dark Mode Support:** System-responsive dark/light theme switching
- **Mobile Responsive:** Optimized for desktop, tablet, and mobile devices
- **Intuitive Navigation:** Role-based menu system with clear visual hierarchy

### ⚡ **Enhanced User Experience**
- **Real-Time Feedback:** Visual indicators for form validation and user actions
- **Keyboard Shortcuts:** Enter key support for quick form submission
- **Loading States:** Progress indicators for better user experience
- **Error Handling:** Comprehensive error messages and validation feedback

## �️ **Technology Stack**

### **Backend Architecture**
- **Django 5.2**: Modern Python web framework with async support
- **PostgreSQL**: Primary database with Supabase cloud hosting
- **Multi-Database Routing**: Custom router for tenant database isolation
- **Django ORM**: Advanced query optimization and relationship management

### **Multi-Tenancy Infrastructure**
- **Supabase PostgreSQL**: Main database for tenant configurations
- **Database-per-Tenant**: Complete data isolation architecture  
- **Custom Middleware**: Subdomain routing and tenant detection
- **Dynamic Database Connections**: Runtime database switching

### **Frontend & UX**
- **Tailwind CSS**: Utility-first responsive design
- **Alpine.js**: Lightweight JavaScript framework
- **AJAX & Fetch API**: Asynchronous data operations
- **Local Storage**: Client-side data persistence and auto-save

### **Development & Deployment**
- **Environment Variables**: Secure configuration management
- **Django Management Commands**: Custom tenant management CLI
- **Git-based Workflow**: Version control with production exclusions
- **Render/Supabase Ready**: Cloud deployment configuration

### **Security & Performance**
- **Role-Based Access Control**: Django groups and permissions
- **CSRF Protection**: Built-in security middleware
- **Database Connection Pooling**: Optimized for multi-tenant workloads
- **Query Optimization**: Efficient database operations

## 🏗️ **Project Architecture**

### **Multi-Tenant Structure**
```
sales_management_project/
├── 🏢 tenants/                   # Multi-tenancy core
│   ├── models.py                 # Tenant configuration model
│   ├── middleware.py             # Subdomain routing
│   ├── db_router.py              # Database routing logic
│   └── management/commands/      # Tenant management CLI
│       ├── create_tenant.py      # Production tenant creation
│       ├── migrate_tenant.py     # Tenant-specific migrations
│       ├── force_migrate_tenant.py # Database reset utility
│       └── manual_setup_tenant.py  # Fallback setup command
├── 📱 sales_app/                 # Sales management module
│   ├── templates/sales_app/      # Sales interface templates
│   ├── static/sales_app/         # Frontend assets
│   ├── models.py                 # Sales data models
│   └── views.py                  # Sales business logic
├── 💰 accounting_app/            # Financial management
│   ├── templates/accounting_app/ # Accounting interfaces
│   ├── models.py                 # Financial data models
│   └── views.py                  # Accounting operations
├── � core/                      # Shared functionality
│   ├── templates/core/           # Base templates
│   └── static/core/              # Global assets
└── ⚙️ sales_management_project/  # Project configuration
    ├── settings.py               # Django settings with multi-DB
    ├── urls.py                   # URL routing
    └── wsgi.py                   # WSGI application
│   │   └── revenue_tracking.html   # Revenue analysis dashboard
│   ├── 🔧 models.py           # Financial models (Expense, ProfitLoss, etc.)
│   ├── 🎭 views.py            # Financial business logic
│   └── 🔗 urls.py             # Accounting URL patterns
├── 🎨 core/                   # Shared components and utilities
│   ├── 🧩 templatetags/       # Custom template filters and tags
│   └── 📋 templates/core/     # Base templates and navigation
├── ⚙️ sales_management_project/ # Project configuration
├── 🗄️ db.sqlite3             # Database file
├── 📦 requirements.txt        # Python dependencies
├── 🎨 tailwind.config.js      # Tailwind CSS configuration
└── 📖 README.md              # This documentation
```

### **Database Models**
- **Product:** Inventory items with pricing and stock levels
- **Invoice:** Main sales record with customer and payment info (enhanced with status tracking)
- **Sale:** Individual line items within invoices
- **AdminLog:** Audit trail for administrative actions
- **StockMovement:** Inventory change tracking
- **ExpenseCategory:** Categorization for business expenses
- **Expense:** Detailed expense records with receipts and vendor info
- **ProfitLossSnapshot:** Monthly financial performance snapshots
- **TaxSettings:** Configurable tax rates and calculations
- **AccountingAuditLog:** Comprehensive audit trail for financial operations

## 🏢 **Multi-Tenancy Support**

### **Organization Isolation**
- **Separate Databases:** Each organization gets its own PostgreSQL database for complete data isolation
- **Subdomain-Based Access:** Access via `org1.yourapp.com`, `org2.yourapp.com`, etc.
- **Independent User Management:** Users, roles, and permissions are organization-specific
- **Multi-Location Support:** Organizations can track performance across multiple locations

### **Tenant Management**
- **Automated Setup:** Create new organizations with a single command
- **Database Migrations:** Automatic schema setup for new tenants
- **Resource Limits:** Configurable user limits per organization
- **Admin Interface:** Centralized tenant management dashboard

### **Scalability**
- **Optimized for 10+ Organizations:** Designed to handle multiple tenants efficiently
- **Database Router:** Intelligent routing ensures data never crosses organizational boundaries
- **Performance Isolation:** Each organization's performance doesn't affect others

### **Tenant Commands**
```bash
# Create a new organization
python manage.py create_tenant "ABC Company" abc admin@abc.com

# List all tenants
python manage.py list_tenants

# Migrate all tenant databases
python manage.py migrate_tenants
```

## 🚀 **Installation & Setup**

### **Prerequisites**
- Python 3.8+ 
- Node.js 14+ (for Tailwind CSS)
- Git

### **Quick Start**
1. **Clone the Repository:**
   ```bash
   git clone https://github.com/akyensamuel/Sales-App.git
   cd Sales-App/sales_management_project
   ```

2. **Create Virtual Environment:**
   ```bash
   python -m venv virtual
   # On Windows:
   virtual\Scripts\activate
   # On macOS/Linux:
   source virtual/bin/activate
   ```

3. **Install Python Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Install Node.js Dependencies:**
   ```bash
   npm install
   ```

5. **Database Setup:**
   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   ```

6. **Create User Groups:**
   ```bash
   python manage.py shell
   ```
   ```python
   from django.contrib.auth.models import Group
   Group.objects.create(name='Admin')
   Group.objects.create(name='Managers') 
   Group.objects.create(name='Cashiers')
   exit()
   ```

7. **Run Development Server:**
   ```bash
   python manage.py runserver
   ```

8. **Access the Application:**
   - Open browser to `http://127.0.0.1:8000/`
   - Login with superuser credentials
   - Access Django admin at `http://127.0.0.1:8000/admin/` to assign users to groups

## 👥 **User Management**

### **Setting Up User Roles:**
1. **Access Django Admin:** `/admin/`
2. **Create Users:** Add users in the Users section
3. **Assign Groups:** Add users to appropriate groups (Admin/Managers/Cashiers)
4. **Test Access:** Login as different users to verify permissions

### **Role Capabilities:**
| Feature | Admin | Manager | Cashier |
|---------|-------|---------|---------|
| Sales Entry | ✅ | ✅ | ✅ |
| Manager Dashboard | ✅ | ✅ | ❌ |
| Invoice Editing | ✅ | ✅ | ❌ |
| Invoice Deletion | ✅ | ✅ | ❌ |
| Print Reports | ✅ | ✅ | ❌ |
| Product Management | ✅ | ❌ | ❌ |
| User Management | ✅ | ❌ | ❌ |
| **Accounting Dashboard** | ✅ | ❌ | ❌ |
| **Expense Management** | ✅ | ❌ | ❌ |
| **Financial Reports** | ✅ | ❌ | ❌ |
| **P&L Analysis** | ✅ | ❌ | ❌ |
| **Revenue Tracking** | ✅ | ❌ | ❌ |
| **Audit Logs** | ✅ | ❌ | ❌ |
| Accounting Dashboard | ✅ | ❌ | ❌ |

## 🖨️ **Print Setup & Configuration**

### **Thermal Printer Setup:**
1. Configure receipt printer for 58mm or 80mm paper
2. Set printer to auto-cut after printing
3. Test with receipt_print template

### **A4 Business Reports:**
1. Use landscape orientation for better table layouts
2. Enable background graphics for professional appearance
3. Set margins to 0.5 inches for optimal content fit

## 🔧 **Configuration Options**

### **Environment Variables:**
Create a `.env` file in the project root:
```env
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=sqlite:///db.sqlite3
```

### **Production Deployment:**
- Set `DEBUG=False`
- Configure proper database (PostgreSQL recommended)
- Set up static file serving with WhiteNoise
- Use environment variables for sensitive settings
- Enable SSL/HTTPS for security

## 🎯 **Usage Guide**

### **Making a Sale:**
1. Navigate to Sales Entry
2. Enter customer information
3. Add products using the search feature
4. Verify stock availability
5. Calculate totals and enter payment
6. Choose "Save" or "Save and Print"

### **Managing Invoices:**
1. Access Manager Dashboard
2. Use search filters to find specific invoices
3. Click invoice rows for detailed views
4. Edit or delete as needed
5. Print reports for record-keeping

### **Generating Reports:**
1. Use date filters to select reporting period
2. Apply customer or invoice filters if needed
3. Click appropriate print button
4. Review report in new tab before printing

### **Using the Accounting Module:**
1. Access Accounting Dashboard (Admin only)
2. View financial overview and KPIs
3. Add expenses with categories and receipts
4. Generate P&L reports for any period
5. Track revenue trends and payment status
6. Monitor outstanding invoices

## 💰 **Accounting Module Guide**

### **Financial Dashboard:**
- **Overview Cards:** Monthly revenue, expenses, profit, and outstanding amounts
- **Quick Actions:** Direct access to expense creation and management
- **Recent Activity:** Latest expenses and financial transactions
- **Navigation:** Easy access to all accounting features

### **Expense Management:**
1. **Adding Expenses:**
   - Choose existing category or create new one
   - Enter amount, date, and description
   - Add vendor and payment method information
   - Include reference numbers and notes
   - Mark recurring expenses for tracking

2. **Expense Categories:**
   - Office Supplies, Travel & Transport, Marketing
   - Utilities, Professional Services, Equipment
   - Rent & Facilities, Insurance, Training
   - Customizable categories for specific business needs

3. **Filtering & Search:**
   - Filter by category, date range, payment method
   - Search descriptions, vendors, and notes
   - Export filtered results for analysis

### **Financial Reports:**
1. **Profit & Loss Reports:**
   - Monthly or annual P&L statements
   - Revenue vs. expense breakdowns
   - Profit margin calculations
   - Category-wise expense analysis
   - Printable professional format

2. **Revenue Analysis:**
   - 12-month revenue trend charts
   - Payment status overview
   - Outstanding invoice tracking
   - Collection aging reports

### **Audit & Compliance:**
- Complete audit trail of all financial activities
- User action logging with timestamps
- Change history tracking
- Export capabilities for external auditing
- IP address logging for security

## 🔍 **Search Features Guide**

The advanced search system supports multiple search strategies:

- **Customer Search:** Partial name matching (case-insensitive)
- **Invoice Search:** Partial invoice number matching
- **Date Filtering:** Single date or date range selection
- **Combined Search:** Multiple criteria with OR logic
- **Quick Filters:** Today's sales, specific date ranges

## 📊 **Reporting Features**

### **Available Reports:**
- **Daily Sales Report:** All invoices for a specific date
- **Search Results Report:** Filtered invoice data
- **Customer Reports:** Sales by customer (via search)
- **Period Reports:** Date range analysis

### **Report Contents:**
- Invoice summary with totals
- Detailed item breakdowns
- Payment status indicators
- Customer information
- Sales representative tracking
- Generation timestamps

## 🛠️ **Troubleshooting**

### **Common Issues:**
1. **Print not working:** Check popup blockers and printer connections
2. **Search not returning results:** Verify date formats and search criteria
3. **Stock validation errors:** Check product inventory levels
4. **Permission denied:** Verify user group assignments
5. **Auto-save not working:** Check browser local storage settings

### **Performance Tips:**
- Regular database cleanup of old invoices
- Optimize large product catalogs with pagination
- Use date filters for large datasets
- Clear browser cache if experiencing loading issues

## 🤝 **Contributing**

### **Development Workflow:**
1. Fork the repository
2. Create feature branch: `git checkout -b feature-name`
3. Make changes and test thoroughly
4. Commit with descriptive messages
5. Push and create pull request

### **Code Standards:**
- Follow Django best practices
- Use Tailwind CSS for styling
- Write descriptive comments
- Test all user roles and permissions
- Ensure responsive design compatibility

## 📝 **License**

MIT License - see LICENSE file for details

## 🚀 **Future Enhancements**

### **Sales & Inventory:**
- PDF export functionality
- Email invoice delivery
- Advanced inventory management
- Barcode scanning integration
- Multi-location support

### **Accounting & Finance:**
- Automated tax calculations and filing
- Bank integration for transaction import
- Advanced financial forecasting
- Budget planning and variance analysis
- Integration with accounting software (QuickBooks, Xero)
- Automated recurring expense handling
- Advanced financial dashboards with charts
- Cash flow analysis and projections

### **System & Integration:**
- Customer relationship management
- API development for integrations
- Advanced analytics and dashboards
- Multi-currency support
- Cloud deployment options

---

**Version:** 2.0.0  
**Last Updated:** August 2025  
**Maintainer:** Samuel Akyensah  
**Status:** Not quite Ready
