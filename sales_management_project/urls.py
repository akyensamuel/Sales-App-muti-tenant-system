from django.contrib import admin
from django.urls import path, include
import core.views as core_views
urlpatterns = [
    path('', core_views.Index.as_view(), name='home'),  # Default route
    path('logout_to_home/', core_views.logout_to_home, name='logout_to_home'),
    path('admin/', admin.site.urls),
    path('sales/', include('sales_app.urls')),
    path('accounting/', include('accounting_app.urls')),
]
# The above code sets up the URL routing for a Django project, including paths for the admin interface and two applications: sales and accounting.
# It also includes a default route that serves a home page using a template view.