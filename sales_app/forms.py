from django import forms
from .models import Invoice, Sale



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