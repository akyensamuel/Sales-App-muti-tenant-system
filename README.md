# Sales Management Project

A modern Django-based sales management system with group-based permissions, Tailwind CSS UI, and robust navigation for Admin, Manager, and Cashier roles.

## Features
- **User Groups & Permissions:**
  - **Admin:** Full access to all features, dashboards, and settings.
  - **Manager:** Access to manager dashboard and sales entry.
  - **Cashier:** Access to sales entry only.
- **Authentication:** Custom login/logout with group-based redirects.
- **Navigation:**
  - Home button logs out and redirects to home.
  - Manager Dashboard button visible only to Admins/Managers on sales entry page.
- **Modern UI:** Tailwind CSS for responsive, clean design.
- **Apps:**
  - `sales_app`: Sales entry, manager dashboard, receipt printing.
  - `accounting_app`: Accounting dashboard (Admin only).
  - `core`: Shared templates, navigation, custom template tags.

## Project Structure
```
├── accounting_app/
│   ├── templates/accounting_app/
│   ├── models.py, views.py, urls.py, ...
├── core/
│   ├── templates/core/
│   ├── templatetags/group_filters.py
│   ├── models.py, views.py, urls.py, ...
├── sales_app/
│   ├── templates/sales_app/
│   ├── models.py, views.py, urls.py, forms.py, ...
├── sales_management_project/
│   ├── settings.py, urls.py, ...
├── db.sqlite3
├── manage.py
├── package.json
├── tailwind.config.js
```

## Setup Instructions
1. **Clone the repository:**
   ```sh
   git clone <repo-url>
   cd Sales_App
   ```
2. **Create and activate a virtual environment:**
   ```sh
   python -m venv virtual
   virtual\Scripts\activate
   ```
3. **Install dependencies:**
   ```sh
   pip install -r requirements.txt
   npm install
   ```
4. **Apply migrations:**
   ```sh
   python manage.py migrate
   ```
5. **Create superuser (for Admin access):**
   ```sh
   python manage.py createsuperuser
   ```
6. **Run the development server:**
   ```sh
   python manage.py runserver
   ```
7. **Access the app:**
   - Visit `http://127.0.0.1:8000/` in your browser.

## Customization
- **Groups:**
  - Set up user groups (Admin, Managers, Cashiers) in the Django admin panel.
- **Permissions:**
  - Assign users to groups for role-based access.
- **Styling:**
  - Tailwind CSS config in `tailwind.config.js` and `core/static/css/`.

## Key Files
- `core/templatetags/group_filters.py`: Custom template filter for group checks.
- `core/templates/core/navbar.html`: Navigation bar with group-based button visibility.
- `sales_app/views.py`: Group-based login redirects and dashboard protection.
- `sales_management_project/urls.py`: Main URL routing.

## Notes
- **Development Only:** Do not use the Django dev server in production. See [Django deployment docs](https://docs.djangoproject.com/en/5.2/howto/deployment/).
- **Database:** Uses SQLite by default. Change `DATABASES` in `settings.py` for production.

## License
MIT License
