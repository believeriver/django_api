# api_portfolio/serializers.py
from rest_framework import serializers
from .models import Portfolio


class PortfolioRecordSerializer(serializers.ModelSerializer):
    """購入履歴1件"""

    class Meta:
        model  = Portfolio
        fields = [
            'id',
            'shares',
            'purchase_price',
            'purchased_at',
            'memo',
            'account_type',   # ← 追加
        ]


class PortfolioSerializer(serializers.ModelSerializer):
    """銘柄追加・更新用"""
    company_code = serializers.CharField(source='company_id')
    company_name = serializers.CharField(source='company.name', read_only=True)

    class Meta:
        model  = Portfolio
        fields = [
            'id',
            'company_code',
            'company_name',
            'shares',
            'purchase_price',
            'purchased_at',
            'memo',
            'account_type',   # ← 追加
        ]
        read_only_fields = ['id', 'company_name']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class PortfolioSummarySerializer(serializers.Serializer):
    """企業ごとの集計（一覧表示用）"""
    company_code       = serializers.CharField()
    company_name       = serializers.CharField()
    total_shares       = serializers.IntegerField()
    avg_purchase_price = serializers.DecimalField(max_digits=10, decimal_places=2)
    records            = PortfolioRecordSerializer(many=True)