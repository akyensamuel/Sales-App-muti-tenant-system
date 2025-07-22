from django import forms
from .models import Invoice, Sale, Product

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'price', 'stock']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'w-full rounded border-gray-300 dark:border-gray-700 bg-gray-50 dark:bg-gray-700 text-gray-900 dark:text-white px-3 py-2 focus:outline-none focus:ring-2 focus:ring-green-500'}),
            'price': forms.NumberInput(attrs={'class': 'w-full rounded border-gray-300 dark:border-gray-700 bg-gray-50 dark:bg-gray-700 text-gray-900 dark:text-white px-3 py-2 focus:outline-none focus:ring-2 focus:ring-green-500', 'step': '0.01'}),
            'stock': forms.NumberInput(attrs={'class': 'w-full rounded border-gray-300 dark:border-gray-700 bg-gray-50 dark:bg-gray-700 text-gray-900 dark:text-white px-3 py-2 focus:outline-none focus:ring-2 focus:ring-green-500'}),
        }



class InvoiceForm(forms.ModelForm):
    class Meta:
        model = Invoice
        # Remove 'discount' from fields
        fields = ['customer_name', 'date_of_sale', 'notes', 'amount_paid']
        widgets = {
            'customer_name': forms.TextInput(attrs={'class': 'form-control'}),
            'date_of_sale': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'amount_paid': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }

class SaleForm(forms.ModelForm):
    class Meta:
        model = Sale
        fields = ['item', 'unit_price', 'quantity', 'discount', 'total_price']
        widgets = {
            'item': forms.TextInput(attrs={'class': 'form-control'}),
            'unit_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control'}),
            'discount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'total_price': forms.NumberInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
        }