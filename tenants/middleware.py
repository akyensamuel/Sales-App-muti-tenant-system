from django.http import Http404, HttpResponse
from django.shortcuts import render
from django.conf import settings
from .models import Tenant
import threading
import sys

# Thread-local storage for current tenant
_thread_local = threading.local()


class TenantMiddleware:
    """
    Middleware to enforce tenant-only access through subdomains.
    
    URL structure:
    - tenant1.localhost:8000 -> routes to tenant1's database
    - admin.localhost:8000 -> routes to main admin interface  
    - localhost:8000 or 127.0.0.1:8000 -> shows tenant selection page
    
    All application functionality requires a valid tenant subdomain.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Extract subdomain from request
        host = request.get_host().split(':')[0]  # Remove port if present
        host_parts = host.split('.')
        
        # Determine subdomain
        if len(host_parts) >= 2:
            subdomain = host_parts[0]
        else:
            # No subdomain (localhost, 127.0.0.1) - show tenant selection
            subdomain = None
        
        # Handle different access patterns
        if subdomain == 'admin':
            # Admin interface access - allow without tenant
            set_current_tenant(None)
            request.tenant = None
            
        elif subdomain:
            # Tenant subdomain - validate and load tenant
            try:
                tenant = Tenant.objects.get(subdomain=subdomain, is_active=True)
                set_current_tenant(tenant)
                request.tenant = tenant
                
                # Ensure tenant database is loaded in settings
                from .utils import ensure_tenant_database_loaded
                ensure_tenant_database_loaded(tenant)
                
            except Tenant.DoesNotExist:
                # Invalid tenant subdomain
                return self._render_tenant_error(request, subdomain)
                
        else:
            # No subdomain - check if path requires tenant
            if request.path.startswith('/admin/'):
                # Allow admin access without subdomain
                set_current_tenant(None)
                request.tenant = None
            elif request.path in ['/', '/favicon.ico']:
                # Allow home page and favicon without tenant
                set_current_tenant(None)
                request.tenant = None
            elif request.path.startswith(('/sales/', '/accounting/')):
                # Tenant-specific apps - show tenant selection immediately
                set_current_tenant(None)
                request.tenant = None
                return self._render_tenant_selection(request)
            else:
                # For all other paths, also show tenant selection to be safe
                set_current_tenant(None)
                request.tenant = None
                return self._render_tenant_selection(request)
        
        response = self.get_response(request)
        return response
    
    def _render_tenant_selection(self, request):
        """Render tenant selection page for main domain access"""
        try:
            tenants = Tenant.objects.filter(is_active=True).order_by('name')
            context = {
                'tenants': tenants,
                'current_host': request.get_host(),
                'requested_path': request.path,  # Add the requested path
            }
            return render(request, 'tenants/tenant_selection.html', context)
        except Exception:
            # If tenants table doesn't exist (first migration), show simple message
            return HttpResponse(f"""
                <html>
                <head><title>Tenant Selection</title></head>
                <body>
                    <h1>Multi-Tenant Sales Management System</h1>
                    <p>You tried to access: <strong>{request.path}</strong></p>
                    <p>This application requires access through a tenant subdomain:</p>
                    <ul>
                        <li><a href="http://demo.localhost:8000{request.path}">demo.localhost:8000{request.path}</a> - Demo Company</li>
                        <li><a href="http://test.localhost:8000{request.path}">test.localhost:8000{request.path}</a> - Test Company</li>
                        <li><a href="http://dev.localhost:8000{request.path}">dev.localhost:8000{request.path}</a> - Development Corp</li>
                    </ul>
                    <p><small>Note: You may need to add these domains to your hosts file for local development.</small></p>
                </body>
                </html>
            """, content_type='text/html')
    
    def _render_tenant_error(self, request, subdomain):
        """Render error page for invalid tenant subdomain"""
        return HttpResponse(f"""
            <html>
            <head><title>Tenant Not Found</title></head>
            <body>
                <h1>Tenant Not Found</h1>
                <p>The tenant subdomain '<strong>{subdomain}</strong>' was not found or is not active.</p>
                <p><a href="http://{request.get_host().split('.')[1] if '.' in request.get_host() else request.get_host().split(':')[0]}:8000">← Back to tenant selection</a></p>
            </body>
            </html>
        """, status=404, content_type='text/html')


def get_current_tenant():
    """Get the current tenant from thread-local storage"""
    return getattr(_thread_local, 'tenant', None)


def set_current_tenant(tenant):
    """Set the current tenant in thread-local storage"""
    _thread_local.tenant = tenant


def tenant_required(view_func):
    """
    Decorator to require a valid tenant for a view.
    Redirects to tenant selection if no tenant is found.
    """
    def wrapper(request, *args, **kwargs):
        if not hasattr(request, 'tenant') or request.tenant is None:
            # Redirect to tenant selection page or show error
            from django.http import HttpResponse
            return HttpResponse(
                "Please access this application through a valid tenant subdomain.",
                status=400
            )
        return view_func(request, *args, **kwargs)
    return wrapper
