from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse, HttpResponse
from django.db.models import Sum
from django.utils import timezone
from django import forms
from decimal import Decimal
from django.db import transaction
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.forms import inlineformset_factory

from .models import Product, Invoice, Sale, AdminLog
from .forms import InvoiceForm, SaleForm


# Utility function to check if user is a manager
def is_manager(user):
    return user.is_authenticated and user.groups.filter(name='Managers').exists()


# === AUTH VIEWS ===
def login_view(request):
    if request.user.is_authenticated:
        if request.user.groups.filter(name='Managers').exists():
            return redirect('manager_dashboard')
        return redirect('sales_entry')

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            if user.groups.filter(name='Managers').exists():
                return redirect('manager_dashboard')
            return redirect('sales_entry')
        else:
            return render(request, 'sales_app/login.html', {'error': 'Invalid credentials'})
    return render(request, 'sales_app/login.html')


def logout_view(request):
    logout(request)
    return redirect('login')


# === PRODUCT MANAGEMENT VIEWS ===
class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'price', 'stock']


@login_required
@user_passes_test(is_manager)
def products_list(request):
    products = Product.objects.all().order_by('name')
    return render(request, 'sales_app/products.html', {'products': products})


@login_required
@user_passes_test(is_manager)
def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('products_list')
    else:
        form = ProductForm()
    return render(request, 'sales_app/product_form.html', {'form': form, 'action': 'Add'})


@login_required
@user_passes_test(is_manager)
def edit_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            return redirect('products_list')
    else:
        form = ProductForm(instance=product)
    return render(request, 'sales_app/product_form.html', {'form': form, 'action': 'Edit'})


@login_required
@user_passes_test(is_manager)
def delete_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        product.delete()
        return redirect('products_list')
    return render(request, 'sales_app/product_confirm_delete.html', {'product': product})


# === PRODUCT SEARCH API ===
def product_autocomplete(request):
    q = request.GET.get('q', '')
    products = Product.objects.filter(name__icontains=q)[:10]
    data = [
        {
            'id': p.id, 
            'name': p.name, 
            'unit_price': str(p.price),
            'stock': p.stock or 0  # Include stock information
        }
        for p in products
    ]
    return JsonResponse(data, safe=False)


def product_search_api(request):
    """
    API endpoint for Select2 product search.
    Expects a 'q' GET parameter for the search term.
    Returns JSON list of matching products with id, name, price, and stock.
    """
    if request.method == 'GET':
        query = request.GET.get('q', '').strip()
        if query:
            products = Product.objects.filter(name__icontains=query)[:20]
        else:
            products = Product.objects.none()
        data = [
            {
                'id': product.id,
                'text': product.name,
                'price': str(product.price),
                'unit_price': str(product.price),  # Keep both for compatibility
                'stock': product.stock or 0
            }
            for product in products
        ]
        return JsonResponse(data, safe=False)
    return JsonResponse([], safe=False)


def validate_stock_availability(formset_data):
    """
    Validate that all items in the formset have sufficient stock.
    Returns a list of error messages if validation fails.
    """
    errors = []
    stock_requirements = {}  # {product_name: total_quantity_needed}
    
    for form_data in formset_data:
        if form_data and not form_data.get('DELETE', False):
            item_name = form_data.get('item')
            quantity = form_data.get('quantity', 0)
            
            if item_name and quantity > 0:
                if item_name in stock_requirements:
                    stock_requirements[item_name] += quantity
                else:
                    stock_requirements[item_name] = quantity
    
    # Check stock availability for each product
    for item_name, total_needed in stock_requirements.items():
        try:
            product = Product.objects.get(name=item_name)
            if product.stock is None or product.stock < total_needed:
                available = product.stock or 0
                errors.append(
                    f"Insufficient stock for '{item_name}'. "
                    f"Needed: {total_needed}, Available: {available}"
                )
        except Product.DoesNotExist:
            errors.append(f"Product '{item_name}' not found in inventory.")
    
    return errors


def deduct_stock_for_sale_items(formset_data, invoice_no):
    """
    Deduct stock quantities for all items in the sale.
    This function should be called within a database transaction.
    """
    stock_deductions = {}  # {product_name: total_quantity_to_deduct}
    
    # Calculate total deductions needed per product
    for form_data in formset_data:
        if form_data and not form_data.get('DELETE', False):
            item_name = form_data.get('item')
            quantity = form_data.get('quantity', 0)
            
            if item_name and quantity > 0:
                if item_name in stock_deductions:
                    stock_deductions[item_name] += quantity
                else:
                    stock_deductions[item_name] = quantity
    
    # Apply deductions
    for item_name, total_deduction in stock_deductions.items():
        try:
            product = Product.objects.select_for_update().get(name=item_name)
            product.stock = (product.stock or 0) - total_deduction
            product.save()
            
            print(f"Stock deducted: {item_name} - {total_deduction} units. New stock: {product.stock}")
            
        except Product.DoesNotExist:
            # This shouldn't happen if validation was done properly
            print(f"WARNING: Product '{item_name}' not found during stock deduction")


def restore_stock_for_sale_items(sale_items, invoice_no):
    """
    Restore stock quantities for sale items (used when deleting/editing invoices).
    """
    for sale_item in sale_items:
        if sale_item.item and sale_item.quantity:
            try:
                product = Product.objects.select_for_update().get(name=sale_item.item)
                product.stock = (product.stock or 0) + sale_item.quantity
                product.save()
                
                print(f"Stock restored: {sale_item.item} + {sale_item.quantity} units. New stock: {product.stock}")
                
            except Product.DoesNotExist:
                print(f"WARNING: Product '{sale_item.item}' not found during stock restoration")


# === SALES ENTRY VIEW ===
@login_required
def sales_entry(request):
    SaleFormSet = inlineformset_factory(Invoice, Sale, form=SaleForm, extra=1, can_delete=True)
    
    if request.method == 'POST':
        print("=== DEBUG: Form submitted ===")
        print("POST data:", request.POST)
        print("save_print in POST:", 'save_print' in request.POST)
        
        invoice_form = InvoiceForm(request.POST)
        formset = SaleFormSet(request.POST)
        
        print("Invoice form valid:", invoice_form.is_valid())
        if not invoice_form.is_valid():
            print("Invoice form errors:", invoice_form.errors)
            
        print("Formset valid:", formset.is_valid())
        if not formset.is_valid():
            print("Formset errors:", formset.errors)
            
        if invoice_form.is_valid() and formset.is_valid():
            # Validate stock availability before proceeding
            formset_data = [form.cleaned_data for form in formset if form.cleaned_data]
            stock_errors = validate_stock_availability(formset_data)
            
            if stock_errors:
                # Add error messages and re-render form
                for error in stock_errors:
                    messages.error(request, error)
                print("=== DEBUG: Stock validation failed ===")
                print("Stock errors:", stock_errors)
            else:
                # Use database transaction to ensure data consistency
                try:
                    with transaction.atomic():
                        print("=== DEBUG: Both forms valid and stock available, saving ===")
                        invoice = invoice_form.save(commit=False)
                        invoice.user = request.user
                        
                        # Calculate total
                        total = Decimal('0.00')
                        for form in formset:
                            if form.cleaned_data and not form.cleaned_data.get('DELETE', False):
                                item_total = form.cleaned_data.get('total_price') or Decimal('0.00')
                                total += item_total
                        
                        invoice.save()  # Save invoice to get ID
                        
                        # Deduct stock before saving formset
                        deduct_stock_for_sale_items(formset_data, invoice.invoice_no)
                        
                        # Save the formset
                        formset.instance = invoice
                        formset.save()
                        
                        # Recalculate total from saved items
                        invoice.total = sum(item.total_price for item in invoice.items.all())
                        invoice.save()
                        
                        messages.success(request, f'Invoice {invoice.invoice_no} saved successfully!')
                        
                        if 'save_print' in request.POST:
                            print("=== DEBUG: Save and Print clicked, rendering receipt ===")
                            context = {
                                'invoice': invoice,
                                'items': invoice.items.all(),
                            }
                            return render(request, 'sales_app/receipt_print.html', context)
                        
                        return redirect('sales_entry')
                        
                except Exception as e:
                    # If anything goes wrong, the transaction will be rolled back
                    messages.error(request, f'Error saving invoice: {str(e)}')
                    print(f"=== DEBUG: Error during save: {e} ===")
        else:
            print("=== DEBUG: Form validation failed ===")
    else:
        invoice_form = InvoiceForm()
        formset = SaleFormSet()
    
    return render(request, 'sales_app/sales_entry.html', {
        'invoice_form': invoice_form,
        'formset': formset
    })


# === MANAGER DASHBOARD & INVOICE VIEWS ===
@login_required
@user_passes_test(is_manager)
def manager_dashboard(request):
    invoices = Invoice.objects.all().order_by('-date_of_sale')
    
    # Get search parameters
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    customer_name = request.GET.get('customer_name', '').strip()
    invoice_no = request.GET.get('invoice_no', '').strip()
    
    # Check if any search parameters are provided
    has_search_params = any([start_date, end_date, customer_name, invoice_no])
    
    if has_search_params:
        # Build OR conditions using Q objects
        from django.db.models import Q
        search_conditions = Q()
        
        # Date range search
        if start_date and end_date:
            search_conditions |= Q(date_of_sale__gte=start_date, date_of_sale__lte=end_date)
        elif start_date:
            search_conditions |= Q(date_of_sale__gte=start_date)
        elif end_date:
            search_conditions |= Q(date_of_sale__lte=end_date)
        
        # Customer name search (case-insensitive partial match)
        if customer_name:
            search_conditions |= Q(customer_name__icontains=customer_name)
        
        # Invoice number search (case-insensitive partial match)
        if invoice_no:
            search_conditions |= Q(invoice_no__icontains=invoice_no)
        
        # Apply the OR search conditions
        if search_conditions:
            invoices = invoices.filter(search_conditions)
    else:
        # Default behavior: show today's invoices if no search parameters
        today = timezone.now().date()
        invoices = invoices.filter(date_of_sale=today)

    # Handle invoice deletion with stock restoration
    if request.method == 'POST' and 'delete_invoice_id' in request.POST:
        invoice_id = request.POST.get('delete_invoice_id')
        try:
            with transaction.atomic():
                invoice = Invoice.objects.get(id=invoice_id)
                
                # Restore stock for all items in the invoice
                restore_stock_for_sale_items(invoice.items.all(), invoice.invoice_no)
                
                # Log the deletion
                AdminLog.objects.create(
                    user=request.user,
                    action='Deleted Invoice (Stock Restored)',
                    details=f'Invoice ID: {invoice_id}, Customer: {invoice.customer_name}'
                )
                
                invoice.delete()
                messages.success(request, f'Invoice deleted and stock quantities restored.')
                
        except Invoice.DoesNotExist:
            messages.error(request, 'Invoice not found.')
        except Exception as e:
            messages.error(request, f'Error deleting invoice: {str(e)}')
            
        return redirect('manager_dashboard')

    total_sales = invoices.aggregate(Sum('total'))['total__sum'] or 0
    return render(request, 'sales_app/manager_dashboard.html', {
        'invoices': invoices,
        'total_sales': total_sales,
        'search_params': {
            'start_date': start_date,
            'end_date': end_date,
            'customer_name': customer_name,
            'invoice_no': invoice_no,
        }
    })


@login_required
@user_passes_test(is_manager)
def print_daily_invoices(request):
    """Print all invoices for a specific date"""
    date_str = request.GET.get('date')
    if not date_str:
        # Default to today
        print_date = timezone.now().date()
    else:
        try:
            from datetime import datetime
            print_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            print_date = timezone.now().date()
    
    invoices = Invoice.objects.filter(date_of_sale=print_date).prefetch_related('items').order_by('invoice_no')
    total_sales = invoices.aggregate(Sum('total'))['total__sum'] or 0
    
    context = {
        'invoices': invoices,
        'total_sales': total_sales,
        'print_date': print_date,
        'print_type': 'daily'
    }
    return render(request, 'sales_app/invoices_print.html', context)


@login_required
@user_passes_test(is_manager)
def print_search_results(request):
    """Print search results from manager dashboard"""
    # Get the same search parameters as manager_dashboard
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    customer_name = request.GET.get('customer_name', '').strip()
    invoice_no = request.GET.get('invoice_no', '').strip()
    
    invoices = Invoice.objects.all().prefetch_related('items').order_by('-date_of_sale')
    
    # Apply the same search logic as manager_dashboard
    has_search_params = any([start_date, end_date, customer_name, invoice_no])
    
    if has_search_params:
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
        
        if search_conditions:
            invoices = invoices.filter(search_conditions)
    else:
        # If no search params, show today's invoices
        today = timezone.now().date()
        invoices = invoices.filter(date_of_sale=today)
    
    total_sales = invoices.aggregate(Sum('total'))['total__sum'] or 0
    
    context = {
        'invoices': invoices,
        'total_sales': total_sales,
        'search_params': {
            'start_date': start_date,
            'end_date': end_date,
            'customer_name': customer_name,
            'invoice_no': invoice_no,
        },
        'print_type': 'search'
    }
    return render(request, 'sales_app/invoices_print.html', context)


@login_required
@user_passes_test(is_manager)
def invoice_detail(request, invoice_id, print_mode=False):
    invoice = get_object_or_404(Invoice, id=invoice_id)
    items = invoice.items.exclude(item__isnull=True).exclude(item__exact="")
    if print_mode or request.resolver_match.url_name == 'receipt_print':
        return render(request, 'sales_app/receipt_print.html', {
            'invoice': invoice,
            'items': items
        })
    return render(request, 'sales_app/invoice_detail.html', {
        'invoice': invoice,
        'items': items
    })


@login_required
@user_passes_test(is_manager)
def edit_invoice(request, invoice_id):
    invoice = get_object_or_404(Invoice, id=invoice_id)
    SaleFormSet = inlineformset_factory(Invoice, Sale, form=SaleForm, extra=0, can_delete=True)
    
    if request.method == 'POST':
        form = InvoiceForm(request.POST, instance=invoice)
        formset = SaleFormSet(request.POST, instance=invoice)
        
        if form.is_valid() and formset.is_valid():
            try:
                with transaction.atomic():
                    # First, restore stock for the original invoice items
                    original_items = list(invoice.items.all())
                    restore_stock_for_sale_items(original_items, invoice.invoice_no)
                    
                    # Validate stock for new/updated items
                    formset_data = [form.cleaned_data for form in formset if form.cleaned_data]
                    stock_errors = validate_stock_availability(formset_data)
                    
                    if stock_errors:
                        # Restore the original stock deductions if validation fails
                        for sale_item in original_items:
                            if sale_item.item and sale_item.quantity:
                                try:
                                    product = Product.objects.select_for_update().get(name=sale_item.item)
                                    product.stock = (product.stock or 0) - sale_item.quantity
                                    product.save()
                                except Product.DoesNotExist:
                                    pass
                        
                        for error in stock_errors:
                            messages.error(request, error)
                        raise ValidationError("Stock validation failed")
                    
                    # Save the updated invoice and formset
                    invoice = form.save(commit=False)
                    invoice.user = request.user
                    invoice.save()
                    formset.save()
                    
                    # Deduct stock for the new/updated items
                    deduct_stock_for_sale_items(formset_data, invoice.invoice_no)
                    
                    # Recalculate total after saving
                    items_total = sum(item.total_price or 0 for item in invoice.items.all())
                    invoice_discount = invoice.discount or 0
                    invoice.total = items_total - invoice_discount
                    invoice.save()
                    
                    messages.success(request, 'Invoice updated successfully!')
                    return redirect('manager_dashboard')
                    
            except ValidationError:
                # Error messages already added above
                pass
            except Exception as e:
                messages.error(request, f'Error updating invoice: {str(e)}')
    else:
        form = InvoiceForm(instance=invoice)
        formset = SaleFormSet(instance=invoice)
        
    return render(request, 'sales_app/edit_invoice.html', {
        'form': form,
        'formset': formset,
        'invoice': invoice
    })


@login_required
@user_passes_test(is_manager)
def edit_sale(request, sale_id):
    sale = get_object_or_404(Sale, id=sale_id)
    if request.method == 'POST':
        form = SaleForm(request.POST, instance=sale)
        if form.is_valid():
            form.save()
            return redirect('manager_dashboard')
    else:
        form = SaleForm(instance=sale)
    return render(request, 'sales_app/edit_sale.html', {'form': form})


# === DEBUG VIEW ===
def test_debug(request):
    print("=== TEST DEBUG VIEW CALLED ===")
    print("This should appear in terminal")
    return HttpResponse("Debug test")