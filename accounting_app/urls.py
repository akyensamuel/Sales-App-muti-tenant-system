from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.accounting_login, name='accounting_login'),
    path('', views.accounting_dashboard, name='accounting_dashboard'),
    path('dashboard/', views.accounting_dashboard, name='dashboard_home'),
    
    # Expense Management
    path('expenses/', views.expense_list, name='expense_list'),
    path('expenses/create/', views.expense_create, name='expense_create'),
    path('expenses/<int:expense_id>/edit/', views.expense_edit, name='expense_edit'),
    path('expenses/<int:expense_id>/delete/', views.expense_delete, name='expense_delete'),
    
    # Reports
    path('reports/profit-loss/', views.profit_loss_report, name='profit_loss_report'),
    path('reports/revenue/', views.revenue_tracking, name='revenue_tracking'),
    
    # Legacy routes for compatibility
    path('forecast_dashboard/', views.forecast_dashboard, name='forecast_dashboard'),
]