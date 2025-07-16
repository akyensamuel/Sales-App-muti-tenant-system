from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='sales_root'),  # Added root path
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('sales_entry/', views.sales_entry, name='sales_entry'),
    path('manager_dashboard/', views.manager_dashboard, name='manager_dashboard'),
    path('edit_sale/<int:sale_id>/', views.edit_sale, name='edit_sale'),
]