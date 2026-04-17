# api_analytics/views.py
import csv
from datetime import timedelta

from django.http import HttpResponse
from django.utils import timezone
from django.db.models import Count, Avg, Q
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from .models import AccessLog, SecurityLog
from .serializers import AccessLogSerializer, SecurityLogSerializer


class IsSuperUser(IsAuthenticated):
    """superuserのみアクセス可能"""
    def has_permission(self, request, view):
        return super().has_permission(request, view) and request.user.is_superuser


class SummaryView(APIView):
    """全体サマリー"""
    permission_classes = [IsSuperUser]

    def get(self, request):
        now       = timezone.now()
        today     = now.date()
        last_7day = now - timedelta(days=7)
        last_30day = now - timedelta(days=30)

        total      = AccessLog.objects.count()
        today_count = AccessLog.objects.filter(
            created_at__date=today
        ).count()
        week_count  = AccessLog.objects.filter(
            created_at__gte=last_7day
        ).count()
        month_count = AccessLog.objects.filter(
            created_at__gte=last_30day
        ).count()

        # サイト別集計
        site_counts = AccessLog.objects.values('site').annotate(
            count=Count('id')
        ).order_by('-count')

        # ステータスコード別集計
        status_counts = AccessLog.objects.values('status_code').annotate(
            count=Count('id')
        ).order_by('status_code')

        # 平均レスポンスタイム
        avg_response = AccessLog.objects.aggregate(
            avg=Avg('response_time')
        )['avg']

        # セキュリティログサマリー
        login_success = SecurityLog.objects.filter(
            action='login_success',
            created_at__gte=last_30day,
        ).count()
        login_failed  = SecurityLog.objects.filter(
            action='login_failed',
            created_at__gte=last_30day,
        ).count()

        return Response({
            'access_logs': {
                'total':             total,
                'today':             today_count,
                'last_7_days':       week_count,
                'last_30_days':      month_count,
                'avg_response_ms':   round(avg_response, 2) if avg_response else 0,
                'by_site':           list(site_counts),
                'by_status_code':    list(status_counts),
            },
            'security_logs': {
                'login_success_30d': login_success,
                'login_failed_30d':  login_failed,
            },
        })


class AccessLogListView(APIView):
    """
    アクセスログ一覧（フィルタリング対応）

    クエリパラメータ:
        site        : サイト名で絞り込み  例) ?site=blog
        ip_address  : IPアドレスで絞り込み
        status_code : ステータスコードで絞り込み
        method      : メソッドで絞り込み  例) ?method=GET
        date_from   : 開始日  例) ?date_from=2026-01-01
        date_to     : 終了日  例) ?date_to=2026-12-31
        limit       : 取得件数（デフォルト100）
    """
    permission_classes = [IsSuperUser]

    def get(self, request):
        logs = AccessLog.objects.select_related('user')

        # フィルタリング
        site        = request.query_params.get('site')
        ip_address  = request.query_params.get('ip_address')
        status_code = request.query_params.get('status_code')
        method      = request.query_params.get('method')
        date_from   = request.query_params.get('date_from')
        date_to     = request.query_params.get('date_to')
        limit       = int(request.query_params.get('limit', 100))

        if site:
            logs = logs.filter(site=site)
        if ip_address:
            logs = logs.filter(ip_address=ip_address)
        if status_code:
            logs = logs.filter(status_code=status_code)
        if method:
            logs = logs.filter(method=method.upper())
        if date_from:
            logs = logs.filter(created_at__date__gte=date_from)
        if date_to:
            logs = logs.filter(created_at__date__lte=date_to)

        logs       = logs[:limit]
        serializer = AccessLogSerializer(logs, many=True)
        return Response(serializer.data)

    def delete(self, request):
        """
        アクセスログ一括削除

        クエリパラメータ:
            date_to : この日付以前のログを削除  例) ?date_to=2026-01-01
            site    : サイト指定で削除
        """
        date_to = request.query_params.get('date_to')
        site    = request.query_params.get('site')

        if not date_to and not site:
            return Response(
                {'detail': 'date_to または site を指定してください。'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        logs = AccessLog.objects.all()
        if date_to:
            logs = logs.filter(created_at__date__lte=date_to)
        if site:
            logs = logs.filter(site=site)

        count, _ = logs.delete()
        return Response({'deleted': count}, status=status.HTTP_200_OK)


class SecurityLogListView(APIView):
    """セキュリティログ一覧"""
    permission_classes = [IsSuperUser]

    def get(self, request):
        logs = SecurityLog.objects.select_related('user')

        action     = request.query_params.get('action')
        ip_address = request.query_params.get('ip_address')
        date_from  = request.query_params.get('date_from')
        date_to    = request.query_params.get('date_to')
        limit      = int(request.query_params.get('limit', 100))

        if action:
            logs = logs.filter(action=action)
        if ip_address:
            logs = logs.filter(ip_address=ip_address)
        if date_from:
            logs = logs.filter(created_at__date__gte=date_from)
        if date_to:
            logs = logs.filter(created_at__date__lte=date_to)

        logs       = logs[:limit]
        serializer = SecurityLogSerializer(logs, many=True)
        return Response(serializer.data)


class PopularPagesView(APIView):
    """人気ページランキング"""
    permission_classes = [IsSuperUser]

    def get(self, request):
        site  = request.query_params.get('site')
        limit = int(request.query_params.get('limit', 20))

        logs = AccessLog.objects.filter(method='GET', status_code=200)
        if site:
            logs = logs.filter(site=site)

        ranking = logs.values('path', 'site').annotate(
            count=Count('id'),
            avg_response=Avg('response_time'),
        ).order_by('-count')[:limit]

        return Response(list(ranking))


class DailyAccessView(APIView):
    """日別アクセス数"""
    permission_classes = [IsSuperUser]

    def get(self, request):
        days  = int(request.query_params.get('days', 30))
        site  = request.query_params.get('site')
        since = timezone.now() - timedelta(days=days)

        logs = AccessLog.objects.filter(created_at__gte=since)
        if site:
            logs = logs.filter(site=site)

        daily = logs.extra(
            select={'date': 'date(created_at)'}
        ).values('date').annotate(
            count=Count('id')
        ).order_by('date')

        return Response(list(daily))


class SiteAccessView(APIView):
    """サイト別アクセス数"""
    permission_classes = [IsSuperUser]

    def get(self, request):
        days  = int(request.query_params.get('days', 30))
        since = timezone.now() - timedelta(days=days)

        result = AccessLog.objects.filter(
            created_at__gte=since
        ).values('site').annotate(
            count=Count('id'),
            avg_response=Avg('response_time'),
            error_count=Count('id', filter=Q(status_code__gte=400)),
        ).order_by('-count')

        return Response(list(result))


class ExportCSVView(APIView):
    """
    CSVエクスポート（バックアップ用）

    クエリパラメータ:
        type      : access（デフォルト）or security
        date_from : 開始日
        date_to   : 終了日
        site      : サイト指定
    """
    permission_classes = [IsSuperUser]

    def get(self, request):
        log_type  = request.query_params.get('type', 'access')
        date_from = request.query_params.get('date_from')
        date_to   = request.query_params.get('date_to')
        site      = request.query_params.get('site')

        response = HttpResponse(content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = (
            f'attachment; filename="analytics_{log_type}_{timezone.now().strftime("%Y%m%d")}.csv"'
        )
        # BOM付きUTF-8（Excelで文字化けしない）
        response.write('\ufeff')

        writer = csv.writer(response)

        if log_type == 'security':
            writer.writerow([
                'id', 'action', 'ip_address', 'username',
                'email', 'user_agent', 'created_at',
            ])
            logs = SecurityLog.objects.select_related('user')
            if date_from:
                logs = logs.filter(created_at__date__gte=date_from)
            if date_to:
                logs = logs.filter(created_at__date__lte=date_to)
            for log in logs:
                writer.writerow([
                    log.id,
                    log.action,
                    log.ip_address,
                    log.user.username if log.user else 'anonymous',
                    log.email,
                    log.user_agent,
                    log.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                ])
        else:
            writer.writerow([
                'id', 'path', 'method', 'ip_address', 'username',
                'status_code', 'response_time_ms', 'user_agent',
                'site', 'created_at',
            ])
            logs = AccessLog.objects.select_related('user')
            if date_from:
                logs = logs.filter(created_at__date__gte=date_from)
            if date_to:
                logs = logs.filter(created_at__date__lte=date_to)
            if site:
                logs = logs.filter(site=site)
            for log in logs:
                writer.writerow([
                    log.id,
                    log.path,
                    log.method,
                    log.ip_address,
                    log.user.username if log.user else 'anonymous',
                    log.status_code,
                    log.response_time,
                    log.user_agent,
                    log.site,
                    log.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                ])

        return response
