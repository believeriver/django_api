from rest_framework import serializers
from .models import WatchList, WatchItem
from api_market.models import Company


class WatchItemSerializer(serializers.ModelSerializer):
    company_code     = serializers.CharField(source='company.code', read_only=True)
    company_name     = serializers.CharField(source='company.name', read_only=True)
    company_industry = serializers.SerializerMethodField()
    company_dividend = serializers.FloatField(source='company.dividend', read_only=True)
    alert_label      = serializers.CharField(
                           source='get_alert_status_display', read_only=True
                       )
    price_diff_pct   = serializers.FloatField(read_only=True)

    # 登録時に銘柄コードで指定
    company_code_input = serializers.CharField(write_only=True, required=False)

    class Meta:
        model  = WatchItem
        fields = [
            'id',
            'company_code', 'company_name', 'company_industry', 'company_dividend',
            'company_code_input',
            'target_price', 'current_price',
            'price_diff_pct',
            'alert_status', 'alert_label',
            'memo',
            'created_at', 'updated_at',
        ]

    def get_company_industry(self, obj):
        try:
            return obj.company.information.industry
        except Exception:
            return None
        read_only_fields = [
            'id', 'alert_status',
            'created_at', 'updated_at',
        ]

    def validate_company_code_input(self, value):
        if not Company.objects.filter(code=value).exists():
            raise serializers.ValidationError(
                f'銘柄コード {value} は存在しません'
            )
        return value

    def create(self, validated_data):
        code    = validated_data.pop('company_code_input')
        company = Company.objects.get(code=code)
        return WatchItem.objects.create(company=company, **validated_data)


class WatchListSerializer(serializers.ModelSerializer):
    items      = WatchItemSerializer(many=True, read_only=True)
    item_count = serializers.IntegerField(source='items.count', read_only=True)

    class Meta:
        model  = WatchList
        fields = [
            'id', 'name', 'memo',
            'item_count', 'items',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class WatchListSummarySerializer(serializers.ModelSerializer):
    """一覧表示用（itemsを含まない軽量版）"""
    item_count  = serializers.IntegerField(source='items.count', read_only=True)
    alert_count = serializers.SerializerMethodField()

    class Meta:
        model  = WatchList
        fields = [
            'id', 'name', 'memo',
            'item_count', 'alert_count',
            'created_at', 'updated_at',
        ]

    def get_alert_count(self, obj):
        return obj.items.exclude(alert_status='none').count()
