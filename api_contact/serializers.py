# api_contact/serializers.py
from rest_framework import serializers
from .models import ContactMessage


class ContactMessageCreateSerializer(serializers.ModelSerializer):
    """投稿用（認証不要）"""
    class Meta:
        model  = ContactMessage
        fields = ['id', 'name', 'email', 'subject', 'body']  # ← id追加
        read_only_fields = ['id']


class ContactMessageSerializer(serializers.ModelSerializer):
    """管理者閲覧用"""
    class Meta:
        model  = ContactMessage
        fields = ['id', 'name', 'email', 'subject', 'body', 'is_read', 'created_at']

