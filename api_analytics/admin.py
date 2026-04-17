# api_analytics/admin.py
from django.contrib import admin
from .models import AccessLog, SecurityLog


@admin.register(AccessLog)
class AccessLogAdmin(admin.ModelAdmin):
    list_display    = [
        'path', 'method', 'ip_address', 'status_code',
        'response_time', 'site', 'created_at'
    ]
    list_filter     = ['site', 'method', 'status_code']
    search_fields   = ['path', 'ip_address']
    readonly_fields = ['created_at']


@admin.register(SecurityLog)
class SecurityLogAdmin(admin.ModelAdmin):
    list_display    = [
        'action', 'email', 'ip_address', 'user_agent', 'created_at'
    ]
    list_filter     = ['action']
    search_fields   = ['email', 'ip_address']
    readonly_fields = ['created_at']
