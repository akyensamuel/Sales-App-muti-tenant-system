from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView

urlpatterns = [
    path('', TemplateView.as_view(template_name='home.html'), name='home'),  # Default route
    path('admin/', admin.site.urls),
    path('sales/', include('sales_app.urls')),
    path('accounting/', include('accounting_app.urls')),
]
# The above code sets up the URL routing for a Django project, including paths for the admin interface and two applications: sales and accounting.
# It also includes a default route that serves a home page using a template view.