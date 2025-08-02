from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', include('core.urls')),  # Include core app URLs with namespace
    path('admin/', admin.site.urls),
    path('sales/', include('sales_app.urls')),
    path('accounting/', include('accounting_app.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
# The above code sets up the URL routing for a Django project, including paths for the admin interface and two applications: sales and accounting.
# It also includes a default route that serves a home page using a template view.