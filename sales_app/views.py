# Product management views
def is_manager(user):
    return user.is_authenticated and user.groups.filter(name='Managers').exists()

from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Product
from django import forms

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'price']

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
# Product autocomplete API for sales entry
from django.http import JsonResponse

def product_autocomplete(request):
    q = request.GET.get('q', '')
    products = Product.objects.filter(name__icontains=q)[:10]
    data = [{'id': p.id, 'name': p.name, 'unit_price': str(p.price)} for p in products]
    return JsonResponse(data, safe=False)
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Invoice, Sale, AdminLog
from django.utils import timezone
from datetime import timedelta
from .forms import InvoiceForm, SaleForm
from django.forms import modelformset_factory, inlineformset_factory
from django.db.models import Sum


def is_manager(user):
    return user.is_authenticated and user.groups.filter(name='Managers').exists()

# Product management views
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse, HttpResponseForbidden
from .models import Product

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

def product_autocomplete(request):
    q = request.GET.get('q', '')
    products = Product.objects.filter(name__icontains=q)[:10]
    data = [{'id': p.id, 'name': p.name, 'unit_price': str(p.unit_price)} for p in products]
    return JsonResponse(data, safe=False)

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

@login_required
def sales_entry(request):
    SaleFormSet = inlineformset_factory(Invoice, Sale, form=SaleForm, extra=1, can_delete=True)
    if request.method == 'POST':
        invoice_form = InvoiceForm(request.POST)
        formset = SaleFormSet(request.POST)
        if invoice_form.is_valid() and formset.is_valid():
            invoice = invoice_form.save(commit=False)
            invoice.user = request.user
            total = 0
            from decimal import Decimal
            for form in formset:
                if form.cleaned_data and not form.cleaned_data.get('DELETE', False):
                    item_total = form.cleaned_data.get('total_price')
                    if item_total is None:
                        item_total = Decimal('0.00')
                    total += item_total
            invoice.save()
            formset.instance = invoice
            formset.save()
            invoice.total = sum(item.total_price for item in invoice.items.all())
            invoice.save()
            if 'save_print' in request.POST:
                context = {
                    'invoice': invoice,
                    'items': invoice.items.all(),
                }
                return render(request, 'sales_app/receipt_print.html', context)
            return redirect('sales_entry')
    else:
        invoice_form = InvoiceForm()
        formset = SaleFormSet()
    return render(request, 'sales_app/sales_entry.html', {
        'invoice_form': invoice_form,
        'formset': formset
    })

@login_required
@user_passes_test(is_manager)
def manager_dashboard(request):
    from django.db.models import Q
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    invoices = Invoice.objects.all().order_by('-date_of_sale')
    if start_date:
        invoices = invoices.filter(date_of_sale__gte=start_date)
    if end_date:
        invoices = invoices.filter(date_of_sale__lte=end_date)
    if not start_date and not end_date:
        today = timezone.now().date()
        invoices = invoices.filter(date_of_sale=today)
    if request.method == 'POST' and 'delete_invoice_id' in request.POST:
        invoice_id = request.POST.get('delete_invoice_id')
        try:
            invoice = Invoice.objects.get(id=invoice_id)
            AdminLog.objects.create(user=request.user, action='Deleted Invoice', details=f'Invoice ID: {invoice_id}, Customer: {invoice.customer_name}')
            invoice.delete()
        except Invoice.DoesNotExist:
            pass
        return redirect('manager_dashboard')
    total_sales = invoices.aggregate(Sum('total'))['total__sum'] or 0
    return render(request, 'sales_app/manager_dashboard.html', {
        'invoices': invoices,
        'total_sales': total_sales
    })

@login_required
@user_passes_test(is_manager)
def invoice_detail(request, invoice_id, print_mode=False):
    invoice = Invoice.objects.get(id=invoice_id)
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
    invoice = Invoice.objects.get(id=invoice_id)
    SaleFormSet = inlineformset_factory(Invoice, Sale, form=SaleForm, extra=0, can_delete=True)
    if request.method == 'POST':
        form = InvoiceForm(request.POST, instance=invoice)
        formset = SaleFormSet(request.POST, instance=invoice)
        if form.is_valid() and formset.is_valid():
            invoice = form.save(commit=False)
            invoice.user = request.user
            invoice.save()
            formset.instance = invoice
            formset.save()
            invoice.total = sum(item.total_price for item in invoice.items.all())
            invoice.save()
            return redirect('manager_dashboard')
    else:
        form = InvoiceForm(instance=invoice)
        formset = SaleFormSet(instance=invoice)
    return render(request, 'sales_app/edit_invoice.html', {'form': form, 'formset': formset, 'invoice': invoice})

@user_passes_test(is_manager)
def edit_sale(request, sale_id):
    sale = Sale.objects.get(id=sale_id)
    if request.method == 'POST':
        form = SaleForm(request.POST, instance=sale)
        if form.is_valid():
            form.save()
            return redirect('manager_dashboard')
    else:
        form = SaleForm(instance=sale)
    return render(request, 'sales_app/edit_sale.html', {'form': form})

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



@login_required
def sales_entry(request):
    # Remove 'discount' from InvoiceForm, so only per-item discount is used
    SaleFormSet = inlineformset_factory(Invoice, Sale, form=SaleForm, extra=1, can_delete=True)
    if request.method == 'POST':
        invoice_form = InvoiceForm(request.POST)
        formset = SaleFormSet(request.POST)
        if invoice_form.is_valid() and formset.is_valid():
            invoice = invoice_form.save(commit=False)
            invoice.user = request.user
            # Calculate total from formset using per-item total_price
            total = 0
            from decimal import Decimal
            for form in formset:
                if form.cleaned_data and not form.cleaned_data.get('DELETE', False):
                    item_total = form.cleaned_data.get('total_price')
                    if item_total is None:
                        item_total = Decimal('0.00')
                    total += item_total
            invoice.save()
            formset.instance = invoice
            formset.save()
            # Now recalculate total from all saved items and update invoice
            invoice.total = sum(item.total_price for item in invoice.items.all())
            invoice.save()
            if 'save_print' in request.POST:
                context = {
                    'invoice': invoice,
                    'items': invoice.items.all(),
                }
                return render(request, 'sales_app/receipt_print.html', context)
            return redirect('sales_entry')
    else:
        invoice_form = InvoiceForm()
        formset = SaleFormSet()
    return render(request, 'sales_app/sales_entry.html', {
        'invoice_form': invoice_form,
        'formset': formset
    })




@login_required
@user_passes_test(is_manager)
def manager_dashboard(request):
    from django.db.models import Q
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    invoices = Invoice.objects.all().order_by('-date_of_sale')
    if start_date:
        invoices = invoices.filter(date_of_sale__gte=start_date)
    if end_date:
        invoices = invoices.filter(date_of_sale__lte=end_date)
    if not start_date and not end_date:
        today = timezone.now().date()
        invoices = invoices.filter(date_of_sale=today)
    # Handle delete action (delete all sales for an invoice)
    if request.method == 'POST' and 'delete_invoice_id' in request.POST:
        invoice_id = request.POST.get('delete_invoice_id')
        try:
            invoice = Invoice.objects.get(id=invoice_id)
            AdminLog.objects.create(user=request.user, action='Deleted Invoice', details=f'Invoice ID: {invoice_id}, Customer: {invoice.customer_name}')
            invoice.delete()
        except Invoice.DoesNotExist:
            pass
        return redirect('manager_dashboard')
    total_sales = invoices.aggregate(Sum('total'))['total__sum'] or 0
    return render(request, 'sales_app/manager_dashboard.html', {
        'invoices': invoices,
        'total_sales': total_sales
    })


# Invoice detail view (and print mode)
@login_required
@user_passes_test(is_manager)
def invoice_detail(request, invoice_id, print_mode=False):
    invoice = Invoice.objects.get(id=invoice_id)
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

# Edit invoice view (edit only invoice fields, not items)

@login_required
@user_passes_test(is_manager)
def edit_invoice(request, invoice_id):
    invoice = Invoice.objects.get(id=invoice_id)
    SaleFormSet = inlineformset_factory(Invoice, Sale, form=SaleForm, extra=0, can_delete=True)
    if request.method == 'POST':
        form = InvoiceForm(request.POST, instance=invoice)
        formset = SaleFormSet(request.POST, instance=invoice)
        if form.is_valid() and formset.is_valid():
            invoice = form.save(commit=False)
            invoice.user = request.user
            invoice.save()
            # Save formset, which will handle add, update, and delete
            formset.instance = invoice
            formset.save()
            # Remove any Sale objects not in the formset (should be handled by can_delete)
            # Recalculate invoice total from all current items
            invoice.total = sum(item.total_price for item in invoice.items.all())
            invoice.save()
            return redirect('manager_dashboard')
    else:
        form = InvoiceForm(instance=invoice)
        formset = SaleFormSet(instance=invoice)
    return render(request, 'sales_app/edit_invoice.html', {'form': form, 'formset': formset, 'invoice': invoice})

@user_passes_test(is_manager)
def edit_sale(request, sale_id):
    sale = Sale.objects.get(id=sale_id)
    if request.method == 'POST':
        form = SaleForm(request.POST, instance=sale)
        if form.is_valid():
            form.save()
            return redirect('manager_dashboard')
    else:
        form = SaleForm(instance=sale)
    return render(request, 'sales_app/edit_sale.html', {'form': form})
