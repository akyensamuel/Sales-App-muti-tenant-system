from django import forms
from .models import Product, Sale

class SaleForm(forms.ModelForm):
    class Meta:
        model = Sale
        fields = [
            'job_type', 'unit_price', 'quantity', 'total_price', 'amount_paid', 'balance'
        ]
        widgets = {
            'job_type': forms.TextInput(attrs={'class': 'form-control'}),
            'unit_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control'}),
            'total_price': forms.NumberInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
            'amount_paid': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'balance': forms.NumberInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
        }