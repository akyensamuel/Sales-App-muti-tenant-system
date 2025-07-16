from django.db import models

class FinancialForecast(models.Model):
    job_type = models.CharField(max_length=100)
    projected_revenue = models.DecimalField(max_digits=12, decimal_places=2)
    forecast_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.job_type} - {self.forecast_date}"