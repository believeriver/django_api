from django.contrib import admin
import sys
import os

sys_path = os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))
sys.path.append(sys_path)

from .models import Company, Financial, Information, IndicatorHistory

admin.site.register(Company)
admin.site.register(Financial)
admin.site.register(Information)
admin.site.register(IndicatorHistory)
