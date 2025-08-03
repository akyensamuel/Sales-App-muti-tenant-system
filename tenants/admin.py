from django.contrib import admin
from .models import Tenant, TenantLocation


@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'subdomain', 'database_name', 'is_active', 
        'supports_multi_location', 'max_users', 'created_at'
    ]
    list_filter = ['is_active', 'supports_multi_location', 'created_at']
    search_fields = ['name', 'subdomain', 'admin_email']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'subdomain', 'admin_email')
        }),
        ('Database Configuration', {
            'fields': ('database_name',)
        }),
        ('Settings', {
            'fields': ('is_active', 'max_users', 'supports_multi_location')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )


@admin.register(TenantLocation)
class TenantLocationAdmin(admin.ModelAdmin):
    list_display = ['tenant', 'name', 'code', 'is_active', 'created_at']
    list_filter = ['tenant', 'is_active', 'created_at']
    search_fields = ['name', 'code', 'tenant__name']
    
    fieldsets = (
        ('Location Information', {
            'fields': ('tenant', 'name', 'code', 'address')
        }),
        ('Settings', {
            'fields': ('is_active',)
        })
    )
