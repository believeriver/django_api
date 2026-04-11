# api_portfolio/admin.py
from django.contrib import admin
from .models import Portfolio


@admin.register(Portfolio)
class PortfolioAdmin(admin.ModelAdmin):
    list_display  = [
        'user', 'company', 'shares', 'purchase_price',
        'purchased_at', 'account_type', 'created_at'
    ]
    list_filter   = ['account_type', 'purchased_at']
    search_fields = ['user__email', 'company__code', 'company__name']
    readonly_fields = ['created_at', 'updated_at']
