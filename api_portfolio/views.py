# portfolio/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.db.models import Avg, Sum
from itertools import groupby

from .models import Portfolio
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
