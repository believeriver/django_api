from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.shortcuts import get_object_or_404

from .models import WatchList, WatchItem
from .serializers import (
    WatchListSerializer,
    WatchListSummarySerializer,
    WatchItemSerializer,
)


class WatchListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """自分のウォッチリスト一覧"""
        watchlists = WatchList.objects.filter(user=request.user)
        serializer = WatchListSummarySerializer(watchlists, many=True)
        return Response(serializer.data)

    def post(self, request):
        """ウォッチリスト作成"""
        serializer = WatchListSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class WatchListDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, request, pk):
        return get_object_or_404(WatchList, pk=pk, user=request.user)

    def get(self, request, pk):
        """ウォッチリスト詳細（アイテム含む）"""
        watchlist  = self.get_object(request, pk)
        serializer = WatchListSerializer(watchlist)
        return Response(serializer.data)

    def patch(self, request, pk):
        """ウォッチリスト更新"""
        watchlist  = self.get_object(request, pk)
        serializer = WatchListSerializer(
            watchlist, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request, pk):
        """ウォッチリスト削除"""
        watchlist = self.get_object(request, pk)
        watchlist.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class WatchItemView(APIView):
    permission_classes = [IsAuthenticated]

    def get_watchlist(self, request, watchlist_pk):
        return get_object_or_404(WatchList, pk=watchlist_pk, user=request.user)

    def get(self, request, watchlist_pk):
        """アイテム一覧"""
        watchlist  = self.get_watchlist(request, watchlist_pk)
        serializer = WatchItemSerializer(watchlist.items.all(), many=True)
        return Response(serializer.data)

    def post(self, request, watchlist_pk):
        """アイテム追加"""
        watchlist  = self.get_watchlist(request, watchlist_pk)
        serializer = WatchItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(watchlist=watchlist)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class WatchItemDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, request, watchlist_pk, item_pk):
        watchlist = get_object_or_404(
            WatchList, pk=watchlist_pk, user=request.user
        )
        return get_object_or_404(WatchItem, pk=item_pk, watchlist=watchlist)

    def patch(self, request, watchlist_pk, item_pk):
        """アイテム更新（target_price・current_price・memo）"""
        item       = self.get_object(request, watchlist_pk, item_pk)
        serializer = WatchItemSerializer(
            item, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        # target_price または current_price が更新された場合はアラート再判定
        if 'target_price' in request.data or 'current_price' in request.data:
            item.refresh_from_db()
            item.update_alert_status()

        return Response(WatchItemSerializer(item).data)

    def delete(self, request, watchlist_pk, item_pk):
        """アイテム削除"""
        item = self.get_object(request, watchlist_pk, item_pk)
        item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class WatchItemRefreshView(APIView):
    """現在株価を取得してアラートを更新"""
    permission_classes = [IsAuthenticated]

    def _get_price_from_company(self, item):
        """① Company.stock から取得"""
        try:
            stock = item.company.stock
            if stock:
                return float(stock.replace(',', ''))
        except (ValueError, AttributeError):
            pass
        return None

    def _get_price_from_yfinance(self, code):
        """② yfinance からフォールバック取得"""
        try:
            import yfinance as yf
            data  = yf.Ticker(f'{code}.T')
            price = data.fast_info.get('lastPrice') or \
                    data.fast_info.get('previousClose')
            if price:
                return float(price)
        except Exception:
            pass
        return None

    def post(self, request, watchlist_pk):
        watchlist = get_object_or_404(
            WatchList, pk=watchlist_pk, user=request.user
        )
        items   = watchlist.items.all()
        updated = []
        errors  = []

        for item in items:
            code = item.company.code

            # ① Company.stock から取得
            price  = self._get_price_from_company(item)
            source = 'company'

            # ② yfinance でフォールバック
            if price is None:
                price  = self._get_price_from_yfinance(code)
                source = 'yfinance'

            if price is not None:
                item.current_price = price
                item.save(update_fields=['current_price', 'updated_at'])
                item.update_alert_status()
                updated.append({
                    'code':   code,
                    'price':  price,
                    'source': source,
                })
            else:
                # ③ 取得失敗 → current_price は変更しない（手動入力可能）
                errors.append({
                    'code':  code,
                    'error': '株価取得失敗。手動で入力してください。',
                })

        serializer = WatchListSerializer(watchlist)
        return Response({
            'updated':   updated,
            'errors':    errors,
            'watchlist': serializer.data,
        })
