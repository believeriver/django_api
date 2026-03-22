from rest_framework import serializers
from .models import Company, Financial, Information


class FinancialSerializer(serializers.ModelSerializer):
    """財務データ（全年度グラフ用）"""

    class Meta:
        model = Financial
        fields = [
            'fiscal_year', 'sales', 'operating_margin', 'eps',
            'equity_ratio', 'operating_cash_flow', 'cash_and_equivalents',
            'dividend_per_share', 'payout_ratio'
        ]


class InformationSerializer(serializers.ModelSerializer):
    """指標データ（簡易・詳細両用）"""

    class Meta:
        model = Information
        fields = ['industry', 'description', 'per', 'psr', 'pbr', 'updated_at']


class CompanyListSerializer(serializers.ModelSerializer):
    """一覧用：Company + Information"""
    information = InformationSerializer(read_only=True)

    class Meta:
        model = Company
        fields = [
            'code', 'name', 'stock', 'dividend', 'dividend_rank', 'dividend_update',
            'information'  # 必須：一覧でInformation表示
        ]
        read_only_fields = ['code']


class CompanyDetailSerializer(CompanyListSerializer):
    """詳細用：Company + Information + 全Financial"""
    financials = FinancialSerializer(many=True, read_only=True)

    class Meta(CompanyListSerializer.Meta):
        fields = CompanyListSerializer.Meta.fields + ['financials']
