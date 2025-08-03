from functools import wraps
from django.http import HttpResponse
from tenants.middleware import get_current_tenant


def tenant_required(view_func):
    """
    Decorator to require a valid tenant for a view.
    Redirects to tenant selection if no tenant is found.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        tenant = get_current_tenant()
        if not tenant:
            return HttpResponse(
                """
                <html>
                <head><title>Tenant Required</title></head>
                <body>
                    <h1>Tenant Access Required</h1>
                    <p>This application requires access through a valid tenant subdomain.</p>
                    <p><a href="http://localhost:8000">← Select a tenant</a></p>
                </body>
                </html>
                """,
                status=400,
                content_type='text/html'
            )
        return view_func(request, *args, **kwargs)
    return wrapper
