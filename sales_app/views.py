from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Sale, AdminLog
from django.utils import timezone
from datetime import timedelta
from .forms import SaleForm
from django.db.models import Sum

def is_manager(user):
    return user.is_authenticated and user.groups.filter(name='Managers').exists()

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
    if request.method == 'POST':
        form = SaleForm(request.POST)
        if form.is_valid():
            sale = form.save(commit=False)
            sale.cashier = request.user
            sale.save()


            if 'save_print' in request.POST:
                context = {
                    'recorded_by': request.user.username,
                    'job_type': sale.job_type,
                    'unit_price': sale.unit_price,
                    'quantity': sale.quantity,
                    'total_price': sale.total_price,
                    'amount_paid': sale.amount_paid,
                    'balance': sale.balance,
                    'datetime': sale.sale_date,
                }
                return render(request, 'sales_app/receipt_print.html', context)
            return redirect('sales_entry')
    else:
        form = SaleForm()
    return render(request, 'sales_app/sales_entry.html', {'form': form})



@login_required
@user_passes_test(is_manager)
def manager_dashboard(request):
    # Filter sales from the last 24 hours by default
    now = timezone.now()
    last_24h = now - timedelta(hours=24)
    sales = Sale.objects.filter(sale_date__gte=last_24h).order_by('-sale_date')
    total_sales = sales.aggregate(Sum('total_price'))['total_price__sum'] or 0

    # Handle delete action
    if request.method == 'POST' and 'delete_sale_id' in request.POST:
        sale_id = request.POST.get('delete_sale_id')
        try:
            sale = Sale.objects.get(id=sale_id)
            AdminLog.objects.create(user=request.user, action='Deleted Sale', details=f'Sale ID: {sale_id}, Quantity: {sale.quantity}')
            sale.delete()
        except Sale.DoesNotExist:
            pass
        return redirect('manager_dashboard')

    return render(request, 'sales_app/manager_dashboard.html', {
        'sales': sales,
        'total_sales': total_sales
    })

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
