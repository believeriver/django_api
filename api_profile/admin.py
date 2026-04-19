# api_profile/admin.py
from django.contrib import admin
from .models import Profile, Skill, Career, Link


class SkillInline(admin.TabularInline):
    model  = Skill
    extra  = 1
    fields = ['category', 'name', 'level', 'description', 'order']


class CareerInline(admin.TabularInline):
    model  = Career
    extra  = 1
    fields = ['title', 'company', 'start_date', 'end_date', 'is_current', 'order']


class LinkInline(admin.TabularInline):
    model  = Link
    extra  = 1
    fields = ['platform', 'url', 'label', 'order']


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display  = ['name', 'nickname', 'location', 'is_active', 'updated_at']
    inlines       = [SkillInline, CareerInline, LinkInline]
    readonly_fields = ['created_at', 'updated_at']
