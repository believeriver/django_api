from django.urls import path, include
from . import views
from .views import CompanyDetailFetchView, CompanyDetailView, ScreeningView
from rest_framework.routers import DefaultRouter

app_name = 'api_market'

router = DefaultRouter()
router.register(r'companies', views.CompanyViewSet)

"""
Company API要件：
- 一覧：Company + Information（全件）
- 詳細：Company + Information + 全Financial履歴

    URL例:
    http://127.0.0.1:8000/api/market/companies/
    http://127.0.0.1:8000/api/market/companies/1418/
    http://127.0.0.1:8000/api/market/companies/8963/
"""
"""
例:
  http://127.0.0.1:8000/api/market/stock/7203/
  /api/market/stock/7203/                       -> start は「今日から1年前」
  /api/market/stock/7203/?start=2020-01-01     -> 指定された start を優先
"""
"""
2026-01-01 以降の財務データを分析対象とするスクリーニング API
  POST /api/market/screening/
  認証: 不要
  const response = await fetch('/api/market/screening/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    eps_no_negative:      true,
    dividend_no_zero:     true,
    operating_margin_min: 8.0,
    equity_ratio_min:     40.0,
    dividend_yield_min:   3.0,
    min_years:            null,
    exclude_reit:         false,
    sort_by:              'score',  // 'score' or 'dividend'
  }),
});
const data = await response.json();

"""

urlpatterns = [
    path('', include(router.urls)),
    path('stock/<int:ticker>/', views.stock_price, name='stock-price'),
    path('companies/<str:code>/fetch-detail/',
         CompanyDetailFetchView.as_view(),
         name='company-fetch-detail'),
    path('companies/<str:code>/detail/',
         CompanyDetailView.as_view(),
         name='company-detail'),
    path('screening/', ScreeningView.as_view(), name='screening'),
]