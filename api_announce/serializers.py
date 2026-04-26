# api_announce/serializers.py
from rest_framework import serializers
from django.utils import timezone
from .models import Announcement, ChangeLog


class AnnouncementSerializer(serializers.ModelSerializer):
    type_label   = serializers.CharField(source='get_type_display',   read_only=True)
    status_label = serializers.CharField(source='get_status_display', read_only=True)
    is_active    = serializers.BooleanField(read_only=True)

    class Meta:
        model  = Announcement
        fields = [
            'id', 'title', 'content',
            'type', 'type_label',
            'status', 'status_label',
            'is_pinned', 'is_active',
            'start_at', 'end_at',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ChangeLogSerializer(serializers.ModelSerializer):
    type_label = serializers.CharField(source='get_type_display', read_only=True)

    class Meta:
        model  = ChangeLog
        fields = [
            'id', 'version',
            'type', 'type_label',
            'title', 'content',
            'released_at',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']