from django.contrib import admin
from .models import Invoice, Sale

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('invoice_no', 'customer_name', 'date_of_sale', 'total', 'amount_paid')
    search_fields = ('invoice_no', 'customer_name')

@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ('invoice', 'item', 'unit_price', 'quantity', 'total_price')
    search_fields = ('invoice__invoice_no', 'item')
