from django.urls import path
from . import views

urlpatterns = [
    path('forecasts/', views.forecast_dashboard, name='forecast_dashboard'),
    path('', views.forecast_dashboard, name='forecast_dashboard'),  # Default route for the dashboard
]