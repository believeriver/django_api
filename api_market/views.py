import os
import sys
import datetime
import logging

from django.db.models import Prefetch, Q
from django.http import Http404

from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
# from rest_framework.response import Response
# from rest_framework.pagination import PageNumberPagination
# from django_filters.rest_framework import DjangoFilterBackend


logger = logging.getLogger(__name__)

project_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
logger.debug(f"project route: {project_path}")
sys.path.insert(0, project_path)


from api_market.models import Company, Financial
from api_market.serializers import CompanyListSerializer, CompanyDetailSerializer
from api_market.management.import_stocks import fetch_stock_dataframe


class CompanyViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Company API要件：
    - 一覧：Company + Information（全件）
    - 詳細：Company + Information + 全Financial履歴

        URL例:
        http://127.0.0.1:8000/api_market/companies/
        http://127.0.0.1:8000/api_market/companies/1418/
        http://127.0.0.1:8000/api_market/companies/8963/
    """

    permission_classes = [AllowAny]
    queryset = Company.objects.select_related('information').prefetch_related('financials')
    serializer_class = CompanyListSerializer

    def get_object(self):
        """code=PKで詳細取得（idではない）"""
        code = self.kwargs['pk']  # URL末尾の3205を取得
        queryset = self.get_queryset()
        try:
            return queryset.get(code=code)  # codeで検索！
        except Company.DoesNotExist:
            raise Http404(f"Company code '{code}' not found")

    def get_serializer_class(self):
        """一覧=Company+Information、詳細=全データ"""
        if self.action == 'retrieve':
            return CompanyDetailSerializer
        return CompanyListSerializer

    def get_queryset(self):
        """企業名・コード検索 + 最適プリロード"""
        if self.action == 'retrieve':
            return self.queryset

        # リストのみ検索ソート
        queryset = self.queryset
        # 検索：企業名 or コード（部分一致）
        query = self.request.query_params.get('search', '').strip()
        if query:
            queryset = queryset.filter(
                Q(code__icontains=query) | Q(name__icontains=query)
            )

        # ソート：配当 or コード
        sort = self.request.query_params.get('sort', 'code')
        if sort == 'dividend':
            queryset = queryset.order_by('-dividend', 'code')
        else:
            queryset = queryset.order_by('code')

        return queryset

    def get_serializer_context(self):
        """クエリパラメータ伝播"""
        context = super().get_serializer_context()
        context.update({'request': self.request})
        return context

    @action(detail=False, methods=['get'])
    def search(self, request):
        """検索（銘柄名・コード）"""
        query = request.query_params.get('q', '')
        if not query:
            return Response([])

        companies = Company.objects.select_related('information').filter(
            Q(code__icontains=query) | Q(name__icontains=query)
        )[:20]  # 検索結果上限

        serializer = CompanyListSerializer(companies, many=True)
        return Response(serializer.data)


@api_view(['GET'])
@permission_classes([AllowAny])
def stock_price(request, ticker: int):
    """
    例:
      http://127.0.0.1:8000/api_market/stock/7203/
      /api_market/stock/7203/                       -> start は「今日から1年前」
      /api_market/stock/7203/?start=2020-01-01     -> 指定された start を優先
    """
    today = datetime.date.today()
    # デフォルト: 今日から 1 年前
    # default_start_date = today - datetime.timedelta(days=365)
    default_start_date = today - datetime.timedelta(days=180)
    default_start = default_start_date.isoformat()  # 'YYYY-MM-DD'

    # クエリパラメータ start があればそれを使い、無ければ default_start
    start = request.query_params.get('start', default_start)

    end = today.isoformat()
    span = 365

    try:
        df = fetch_stock_dataframe(ticker, start, end, span)
        logger.info(df)
        data = df.to_dict(orient='records')

        if df.empty:
            return Response(
                {"detail": f"No stock data found for ticker={ticker}"},
                status=404
            )

        if 'value' not in df.columns:
            return Response(
                {"detail": f"Close column not found. columns={list(df.columns)}"},
                status=500
            )

    except Exception as e:
        logger.exception("stock fetch failed: ticker=%s", ticker)
        return Response({"detail": str(e)}, status=500)

    return Response(data)

