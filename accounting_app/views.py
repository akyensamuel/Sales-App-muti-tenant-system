from django.shortcuts import render
from .models import FinancialForecast

def forecast_dashboard(request):
    forecasts = FinancialForecast.objects.all()
    return render(request, 'accounting_app/forecast_dashboard.html', {'forecasts': forecasts})

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test

def is_admin(user):
    return user.is_authenticated and user.groups.filter(name='Admin').exists()

def accounting_login(request):
    if request.user.is_authenticated:
        if is_admin(request.user):
            return redirect('forecast_dashboard')
        return render(request, 'accounting_app/login.html', {'error': 'You do not have permission to access the accounting app.'})

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None and is_admin(user):
            login(request, user)
            return redirect('forecast_dashboard')
        else:
            return render(request, 'accounting_app/login.html', {'error': 'Invalid credentials or insufficient permissions.'})
    return render(request, 'accounting_app/login.html')
