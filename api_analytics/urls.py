# api_analytics/urls.py
from django.urls import path
from .views import (
    SummaryView,
    AccessLogListView,
    SecurityLogListView,
    PopularPagesView,
    DailyAccessView,
    SiteAccessView,
    ExportCSVView,
)

"""
GET    /api/analytics/summary/          全体サマリー
GET    /api/analytics/access-logs/      アクセスログ一覧
DELETE /api/analytics/access-logs/      アクセスログ一括削除
GET    /api/analytics/security-logs/    セキュリティログ一覧
GET    /api/analytics/popular-pages/    人気ページランキング
GET    /api/analytics/daily/            日別アクセス数
GET    /api/analytics/sites/            サイト別集計
GET    /api/analytics/export/           CSVエクスポート
"""

urlpatterns = [
    path('summary/',       SummaryView.as_view(),         name='analytics-summary'),
    path('access-logs/',   AccessLogListView.as_view(),    name='analytics-access-logs'),
    path('security-logs/', SecurityLogListView.as_view(),  name='analytics-security-logs'),
    path('popular-pages/', PopularPagesView.as_view(),     name='analytics-popular-pages'),
    path('daily/',         DailyAccessView.as_view(),      name='analytics-daily'),
    path('sites/',         SiteAccessView.as_view(),       name='analytics-sites'),
    path('export/',        ExportCSVView.as_view(),        name='analytics-export'),
]
