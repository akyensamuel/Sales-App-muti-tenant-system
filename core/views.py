from django.contrib.auth import logout
from django.shortcuts import redirect

def logout_to_home(request):
    logout(request)
    return redirect('core:index')

from django.views import View
from django.shortcuts import render
from django.http import HttpResponse
from tenants.middleware import get_current_tenant


class Index(View):
    def get(self, request):
        # Get current tenant from middleware
        tenant = get_current_tenant()
        
        # Allow home page access without tenant, but redirect to tenant selection for other pages
        if not tenant:
            # This is main domain access - show tenant selection
            from tenants.models import Tenant
            try:
                tenants = Tenant.objects.filter(is_active=True).order_by('name')
                context = {
                    'tenants': tenants,
                    'current_host': request.get_host(),
                    'show_main_site': True,
                }
                return render(request, 'tenants/tenant_selection.html', context)
            except Exception:
                return HttpResponse("""
                    <html>
                    <head><title>Multi-Tenant Sales Management</title></head>
                    <body>
                        <h1>Multi-Tenant Sales Management System</h1>
                        <p>Please access through a tenant subdomain:</p>
                        <ul>
                            <li><a href="http://demo.localhost:8000">demo.localhost:8000</a></li>
                            <li><a href="http://test.localhost:8000">test.localhost:8000</a></li>
                            <li><a href="http://dev.localhost:8000">dev.localhost:8000</a></li>
                        </ul>
                    </body>
                    </html>
                """, content_type='text/html')
        
        context = {
            'tenant': tenant,
            'is_tenant_access': True,
            'tenant_name': tenant.name,
            'tenant_subdomain': tenant.subdomain,
            'tenant_admin_email': tenant.admin_email,
            'tenant_max_users': tenant.max_users,
            'tenant_supports_multi_location': tenant.supports_multi_location,
            'tenant_database': tenant.database_name,
        }
        
        return render(request, 'core/home.html', context)