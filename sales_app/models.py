
from django.db import models
from django.contrib.auth.models import User

class AdminLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    action = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)
    details = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} - {self.action} at {self.timestamp}"

class Product(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Sale(models.Model):
    cashier = models.ForeignKey(User, on_delete=models.CASCADE)
    job_type = models.CharField(max_length=100, default='')
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    quantity = models.IntegerField(default=1)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    sale_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.cashier.username} - {self.quantity} units"
