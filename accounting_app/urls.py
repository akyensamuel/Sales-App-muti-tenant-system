from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.accounting_login, name='accounting_login'),
    path('forecast_dashboard/', views.forecast_dashboard, name='forecast_dashboard'),
    path('', views.forecast_dashboard, name='dashboard_home'),  # Default route for the dashboard
]