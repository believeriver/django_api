# portfolio/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.db.models import Avg, Sum
from itertools import groupby

from .models import Portfolio
from api_market.models import Financial

from .serializers import (
    PortfolioSerializer,
    PortfolioSummarySerializer,
    PortfolioRecordSerializer,
)


class PortfolioListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """企業ごとに集計して一覧返却"""
        records = Portfolio.objects.filter(
            user=request.user
        ).select_related('company')

        # 企業コードでグループ化して集計
        summary = {}
        for record in records:
            code = record.company_id
            if code not in summary:
                summary[code] = {
                    'company_code': code,
                    'company_name': record.company.name,
                    'records':      [],
                }
            summary[code]['records'].append(record)

        # 平均取得単価・合計株数を計算
        result = []
        for code, data in summary.items():
            records_list = data['records']
            total_shares = sum(r.shares for r in records_list)
            avg_price    = sum(
                r.purchase_price * r.shares for r in records_list
            ) / total_shares

            result.append({
                'company_code':      code,
                'company_name':      data['company_name'],
                'total_shares':      total_shares,
                'avg_purchase_price': round(avg_price, 2),
                'records':           records_list,
            })

        serializer = PortfolioSummarySerializer(result, many=True)
        return Response(serializer.data)

    def post(self, request):
        """銘柄追加"""
        serializer = PortfolioSerializer(
            data=request.data,
            context={'request': request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class PortfolioDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk, user):
        """自分のレコードのみ取得できるよう制限"""
        try:
            return Portfolio.objects.get(pk=pk, user=user)
        except Portfolio.DoesNotExist:
            return None

    def get(self, request, pk):
        """購入履歴1件取得"""
        instance = self.get_object(pk, request.user)
        if not instance:
            return Response(
                {'detail': 'Not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = PortfolioSerializer(instance)
        return Response(serializer.data)

    def patch(self, request, pk):
        """購入履歴1件更新"""
        instance = self.get_object(pk, request.user)
        if not instance:
            return Response(
                {'detail': 'Not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = PortfolioSerializer(
            instance,
            data=request.data,
            partial=True,
            context={'request': request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request, pk):
        """購入履歴1件削除"""
        instance = self.get_object(pk, request.user)
        if not instance:
            return Response(
                {'detail': 'Not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class PortfolioDashboardView(APIView):
    permission_classes = [IsAuthenticated]

    """
    企業ごとに集計して返すダッシュボード用API
    response例：
    [
      {
        "company_code": "7203",
        "company_name": "トヨタ自動車",
        "industry": "輸送用機器",
        "per": 8.5,
        "pbr": 1.2,
        "total_shares": 300,
        "avg_purchase_price": 2150.00,
        "dividend_yield": 2.01,
        "dividend_per_share": 60,
        "fiscal_year": "2024-03",
        "dividend_income": 18000.0
      }
    ]
    """

    def get(self, request):
        records = Portfolio.objects.filter(
            user=request.user
        ).select_related(
            'company',
            'company__information',
        )

        # 保有銘柄コードを一括取得
        codes = list(
            records.values_list('company_id', flat=True).distinct()
        )

        # 最新年度の財務データを一括取得（sqlite3対応）
        all_financials = Financial.objects.filter(
            company_id__in=codes
        ).order_by('company_id', '-fiscal_year')

        latest_financials = {}
        for f in all_financials:
            if f.company_id not in latest_financials:
                latest_financials[f.company_id] = f  # 最初の1件が最新年度

        # 企業ごとに集計
        summary = {}
        for record in records:
            code = record.company_id
            if code not in summary:
                company     = record.company
                information = getattr(company, 'information', None)
                financial   = latest_financials.get(code)

                summary[code] = {
                    'company_code':       code,
                    'company_name':       company.name,
                    'dividend_yield':     company.dividend,
                    'industry':           information.industry if information else '未分類',
                    'per':                information.per      if information else None,
                    'pbr':                information.pbr      if information else None,
                    'dividend_per_share': (
                        financial.dividend_per_share if financial else None
                    ),
                    'fiscal_year':        (
                        financial.fiscal_year if financial else None
                    ),
                    'total_shares':       0,
                    'total_cost':         0,
                }
            summary[code]['total_shares'] += record.shares
            summary[code]['total_cost']   += record.purchase_price * record.shares

        # 集計してレスポンス生成
        result = []
        for code, data in summary.items():
            total_shares       = data['total_shares']
            avg_price          = data['total_cost'] / total_shares
            dividend_per_share = data['dividend_per_share']
            dividend_yield     = data['dividend_yield']

            # 配当収入予想（1株配当 → 利回りの順でフォールバック）
            if dividend_per_share:
                # 1株配当ベース（正確）
                dividend_income        = dividend_per_share * total_shares
                dividend_income_source = 'dividend_per_share'
            elif dividend_yield:
                # 配当利回りベース（取得単価基準のため概算）
                dividend_income        = float(avg_price) * total_shares * (dividend_yield / 100)
                dividend_income_source = 'dividend_yield'
            else:
                # データなし
                dividend_income        = 0
                dividend_income_source = None

            result.append({
                'company_code':           code,
                'company_name':           data['company_name'],
                'industry':               data['industry'],
                'per':                    data['per'],
                'pbr':                    data['pbr'],
                'total_shares':           total_shares,
                'avg_purchase_price':     round(float(avg_price), 2),
                'dividend_yield':         dividend_yield,
                'dividend_per_share':     dividend_per_share,
                'fiscal_year':            data['fiscal_year'],
                'dividend_income':        round(float(dividend_income), 2),
                'dividend_income_source': dividend_income_source,
            })

        # 配当収入予想の多い順にソート
        result.sort(key=lambda x: x['dividend_income'], reverse=True)

        return Response(result)


class PortfolioIndustryView(APIView):
    permission_classes = [IsAuthenticated]

    """
    業種別の保有割合を返すAPI（円グラフ用）
    [
      {"industry": "輸送用機器", "total_cost": 645000.0, "ratio": 52.3},
      {"industry": "不動産",    "total_cost": 75000.0,  "ratio": 6.1},
      {"industry": "未分類",    "total_cost": 120000.0, "ratio": 9.7}
    ]
    """

    def get(self, request):
        """業種別の保有割合（円グラフ用）"""
        records = Portfolio.objects.filter(
            user=request.user
        ).select_related(
            'company__information',
        )

        industry_summary = {}
        for record in records:
            info     = getattr(record.company, 'information', None)
            industry = info.industry if info else '未分類'
            cost     = record.purchase_price * record.shares

            if industry not in industry_summary:
                industry_summary[industry] = 0
            industry_summary[industry] += cost

        total = sum(industry_summary.values())
        result = [
            {
                'industry': industry,
                'total_cost': round(float(cost), 2),
                'ratio': round(float(cost) / float(total) * 100, 1),
            }
            for industry, cost in sorted(
                industry_summary.items(),
                key=lambda x: x[1],
                reverse=True,
            )
        ]
        return Response(result)

