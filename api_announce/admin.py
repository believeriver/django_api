# api_announce/admin.py
from django.contrib import admin
from .models import Announcement, ChangeLog


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display  = ['title', 'type', 'status', 'is_pinned', 'start_at', 'end_at', 'created_at']
    list_filter   = ['type', 'status', 'is_pinned']
    search_fields = ['title', 'content']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(ChangeLog)
class ChangeLogAdmin(admin.ModelAdmin):
    list_display  = ['version', 'type', 'title', 'released_at']
    list_filter   = ['type', 'version']
    search_fields = ['title', 'content', 'version']
    readonly_fields = ['created_at', 'updated_at']
