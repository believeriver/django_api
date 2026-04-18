# api_analytics/serializers.py
from rest_framework import serializers
from .models import AccessLog, SecurityLog


class AccessLogSerializer(serializers.ModelSerializer):
    # username = serializers.CharField(
    #     source='user.username', default='anonymous', read_only=True
    # )
    # 変更後（両クラスとも同じ変更）
    username = serializers.CharField(
        source='user.email', default='anonymous', read_only=True
    )

    class Meta:
        model  = AccessLog
        fields = [
            'id', 'path', 'method', 'ip_address', 'username',
            'status_code', 'response_time', 'user_agent',
            'site', 'created_at',
        ]


class SecurityLogSerializer(serializers.ModelSerializer):
    # username = serializers.CharField(
    #     source='user.username', default='anonymous', read_only=True
    # )
    # 変更後（両クラスとも同じ変更）
    username = serializers.CharField(
        source='user.email', default='anonymous', read_only=True
    )

    class Meta:
        model  = SecurityLog
        fields = [
            'id', 'action', 'ip_address', 'username',
            'email', 'user_agent', 'created_at',
        ]
