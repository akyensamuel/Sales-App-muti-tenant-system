from django.core.management.base import BaseCommand
from django.db import transaction
from tenants.models import Tenant
from tenants.utils import switch_tenant_context
from accounting_app.models import ExpenseCategory, Expense
from sales_app.models import Product, Invoice, Sale
from django.contrib.auth.models import User
from decimal import Decimal
import random


class Command(BaseCommand):
    help = 'Create test data for all tenant databases to verify isolation'

    def add_arguments(self, parser):
        parser.add_argument(
            '--tenant',
            type=str,
            help='Create data for specific tenant only',
        )

    def handle(self, *args, **options):
        tenant_filter = options.get('tenant')
        
        self.stdout.write(self.style.SUCCESS('🧪 CREATING TEST DATA FOR TENANT ISOLATION'))
        self.stdout.write('=' * 70)
        
        # Get tenants
        if tenant_filter:
            tenants = Tenant.objects.filter(subdomain=tenant_filter, is_active=True)
        else:
            tenants = Tenant.objects.filter(is_active=True)
        
        if not tenants.exists():
            self.stdout.write(self.style.ERROR('No tenants found'))
            return
        
        for tenant in tenants:
            self.stdout.write(f'\n🏢 Creating test data for: {tenant.name}')
            
            try:
                with switch_tenant_context(tenant):
                    with transaction.atomic():
                        # Create test users
                        self.create_test_users(tenant)
                        
                        # Create accounting test data
                        self.create_accounting_data(tenant)
                        
                        # Create sales test data
                        self.create_sales_data(tenant)
                        
                        # Show summary
                        self.show_tenant_summary(tenant)
                        
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'   ❌ Error: {e}'))
                import traceback
                traceback.print_exc()
        
        self.stdout.write('\n' + '=' * 70)
        self.stdout.write('🎉 Test data creation completed!')
        self.stdout.write('\nNow visit each tenant URL to see isolated data:')
        for tenant in tenants:
            self.stdout.write(f'  • http://{tenant.subdomain}.localhost:8000')

    def create_test_users(self, tenant):
        """Create test users for this tenant"""
        # Create admin user
        admin_user, created = User.objects.get_or_create(
            username=f'{tenant.subdomain}_admin',
            defaults={
                'email': f'admin@{tenant.subdomain}.com',
                'first_name': 'Admin',
                'last_name': tenant.name.split()[0],
                'is_staff': True,
                'is_superuser': True
            }
        )
        if created:
            admin_user.set_password('admin123')
            admin_user.save()
            self.stdout.write(f'   👤 Created admin user: {admin_user.username}')
        
        # Create manager user
        manager_user, created = User.objects.get_or_create(
            username=f'{tenant.subdomain}_manager',
            defaults={
                'email': f'manager@{tenant.subdomain}.com',
                'first_name': 'Manager',
                'last_name': tenant.name.split()[0],
                'is_staff': True
            }
        )
        if created:
            manager_user.set_password('manager123')
            manager_user.save()
            self.stdout.write(f'   👤 Created manager user: {manager_user.username}')

    def create_accounting_data(self, tenant):
        """Create accounting test data"""
        # Create expense categories
        categories_data = [
            ('Office Supplies', f'{tenant.name} office supplies and equipment'),
            ('Marketing', f'{tenant.name} marketing and advertising expenses'),
            ('Travel', f'{tenant.name} business travel expenses'),
            ('Utilities', f'{tenant.name} utilities and office costs'),
        ]
        
        for name, description in categories_data:
            category, created = ExpenseCategory.objects.get_or_create(
                name=name,
                defaults={'description': description}
            )
            if created:
                self.stdout.write(f'   💰 Created expense category: {name}')
        
        # Create sample expenses
        categories = list(ExpenseCategory.objects.all())
        expense_data = [
            ('Office Equipment', random.choice(categories), Decimal('250.00')),
            ('Marketing Campaign', random.choice(categories), Decimal('500.00')),
            ('Business Trip', random.choice(categories), Decimal('300.00')),
            ('Monthly Internet', random.choice(categories), Decimal('75.00')),
        ]
        
        for description, category, amount in expense_data:
            expense = Expense.objects.create(
                description=f'{tenant.name} - {description}',
                category=category,
                amount=amount,
                receipt_date='2025-01-15'
            )
            self.stdout.write(f'   💸 Created expense: {description} (${amount})')

    def create_sales_data(self, tenant):
        """Create sales test data"""
        # Create products specific to this tenant
        products_data = [
            (f'{tenant.name} Premium Widget', Decimal('25.00'), 100),
            (f'{tenant.name} Standard Service', Decimal('50.00'), 200),
            (f'{tenant.name} Professional Package', Decimal('100.00'), 50),
            (f'{tenant.name} Enterprise Solution', Decimal('200.00'), 25),
        ]
        
        for name, price, stock in products_data:
            product, created = Product.objects.get_or_create(
                name=name,
                defaults={'price': price, 'stock': stock}
            )
            if created:
                self.stdout.write(f'   📦 Created product: {name} (${price})')
        
        # Create sample invoices
        products = list(Product.objects.all())
        if products:
            admin_user = User.objects.filter(username__endswith='_admin').first()
            
            invoice = Invoice.objects.create(
                customer_name=f'{tenant.name} Test Customer',
                customer_phone='123-456-7890',
                customer_email=f'customer@{tenant.subdomain}.com',
                total_amount=Decimal('150.00'),
                user=admin_user
            )
            
            # Add sales items to invoice
            for i, product in enumerate(products[:2]):  # Use first 2 products
                Sale.objects.create(
                    invoice=invoice,
                    item=product,
                    quantity=1 + i,
                    unit_price=product.price,
                    total_price=product.price * (1 + i)
                )
            
            self.stdout.write(f'   🧾 Created invoice: {invoice.invoice_no}')

    def show_tenant_summary(self, tenant):
        """Show summary of created data"""
        expense_count = Expense.objects.count()
        category_count = ExpenseCategory.objects.count()
        product_count = Product.objects.count()
        invoice_count = Invoice.objects.count()
        user_count = User.objects.count()
        
        self.stdout.write(f'   📊 Summary for {tenant.name}:')
        self.stdout.write(f'      Users: {user_count}')
        self.stdout.write(f'      Expense Categories: {category_count}')
        self.stdout.write(f'      Expenses: {expense_count}')
        self.stdout.write(f'      Products: {product_count}')
        self.stdout.write(f'      Invoices: {invoice_count}')
