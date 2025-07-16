from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Product, Sale
from .forms import SaleForm
from django.db.models import Sum

def is_manager(user):
    return user.is_authenticated and user.is_staff

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            if user.is_staff:
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
            sale.total_price = sale.quantity * sale.product.price
            sale.product.stock -= sale.quantity
            sale.product.save()
            sale.save()
            return redirect('sales_entry')
    else:
        form = SaleForm()
    return render(request, 'sales_app/sales_entry.html', {'form': form})

@user_passes_test(is_manager)
def manager_dashboard(request):
    sales = Sale.objects.all()
    total_sales = sales.aggregate(Sum('total_price'))['total_price__sum'] or 0
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
