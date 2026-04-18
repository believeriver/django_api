# api_market/views.py
import os
import sys
import datetime
import logging

from django.db.models import Q
from django.http import Http404
from django.core.cache import cache          # ← 追加

from rest_framework import viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

logger = logging.getLogger(__name__)

project_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_path)

from api_market.models import Company, Financial
from api_market.serializers import CompanyListSerializer, CompanyDetailSerializer
from api_market.management.import_stocks import fetch_stock_dataframe


# キャッシュ有効期限
STOCK_CACHE_TTL   = 60 * 15       # 株価データ: 15分
COMPANY_CACHE_TTL = 60 * 60 * 24  # 企業一覧: 24時間


class CompanyViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Company API要件：
    - 一覧：Company + Information（全件）
    - 詳細：Company + Information + 全Financial履歴

    URL例:
        http://127.0.0.1:8000/api/market/companies/
        http://127.0.0.1:8000/api/market/companies/1418/
        http://127.0.0.1:8000/api/market/companies/8963/
    """
    permission_classes = [AllowAny]
    queryset           = Company.objects.select_related(
                             'information'
                         ).prefetch_related('financials')
    serializer_class   = CompanyListSerializer

    def get_object(self):
        code     = self.kwargs['pk']
        queryset = self.get_queryset()
        try:
            return queryset.get(code=code)
        except Company.DoesNotExist:
            raise Http404(f"Company code '{code}' not found")

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return CompanyDetailSerializer
        return CompanyListSerializer

    def get_queryset(self):
        if self.action == 'retrieve':
            return self.queryset

        queryset = self.queryset
        query    = self.request.query_params.get('search', '').strip()
        if query:
            queryset = queryset.filter(
                Q(code__icontains=query) | Q(name__icontains=query)
            )

        sort = self.request.query_params.get('sort', 'code')
        if sort == 'dividend':
            queryset = queryset.order_by('-dividend', 'code')
        else:
            queryset = queryset.order_by('code')

        return queryset

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({'request': self.request})
        return context

    @action(detail=False, methods=['get'])
    def search(self, request):
        query = request.query_params.get('q', '')
        if not query:
            return Response([])

        companies = Company.objects.select_related('information').filter(
            Q(code__icontains=query) | Q(name__icontains=query)
        )[:20]

        serializer = CompanyListSerializer(companies, many=True)
        return Response(serializer.data)


@api_view(['GET'])
@permission_classes([AllowAny])
def stock_price(request, ticker: int):
    """
    株価データを返す。キャッシュ有効期限: 15分。

    URL例:
        /api/market/stock/7203/
        /api/market/stock/7203/?start=2020-01-01
    """
    today        = datetime.date.today()
    default_start = (today - datetime.timedelta(days=180)).isoformat()
    start        = request.query_params.get('start', default_start)
    end          = today.isoformat()
    span         = 365

    # ── キャッシュキー（ticker + start日付で一意に識別）──
    cache_key = f'stock_{ticker}_{start}'
    cached    = cache.get(cache_key)

    if cached is not None:
        # キャッシュヒット → 即返す
        logger.info('cache hit: %s', cache_key)
        return Response(cached)

    # ── キャッシュミス → 外部APIを叩く ──────────────
    logger.info('cache miss: %s → fetching from external API', cache_key)
    try:
        df = fetch_stock_dataframe(ticker, start, end, span)

        if df is None or df.empty:
            return Response(
                {'detail': f'No stock data found for ticker={ticker}'},
                status=404,
            )

        if 'value' not in df.columns:
            return Response(
                {'detail': f'Close column not found. columns={list(df.columns)}'},
                status=500,
            )

        data = df.to_dict(orient='records')

        # ── キャッシュに保存（15分）──────────────────
        cache.set(cache_key, data, timeout=STOCK_CACHE_TTL)
        logger.info('cache set: %s (TTL=%ds)', cache_key, STOCK_CACHE_TTL)

    except Exception as e:
        logger.exception('stock fetch failed: ticker=%s', ticker)
        return Response({'detail': str(e)}, status=500)

    return Response(data)
