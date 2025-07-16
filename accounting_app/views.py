from django.shortcuts import render
from .models import FinancialForecast

def forecast_dashboard(request):
    forecasts = FinancialForecast.objects.all()
    return render(request, 'accounting_app/forecast_dashboard.html', {'forecasts': forecasts})
