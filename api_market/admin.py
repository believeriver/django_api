from django.contrib import admin
import sys
import os

sys_path = os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))
sys.path.append(sys_path)

from .models import Company, Financial, Information, IndicatorHistory, CompanyDetail

admin.site.register(Company)
admin.site.register(Financial)
admin.site.register(Information)
admin.site.register(IndicatorHistory)

@admin.register(CompanyDetail)
class CompanyDetailAdmin(admin.ModelAdmin):
    list_display  = ['company', 'fetched_at', 'updated_at']
    search_fields = ['company__code', 'company__name']
    readonly_fields = ['fetched_at', 'created_at', 'updated_at']
