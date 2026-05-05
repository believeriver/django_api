from django.urls import path, include
from . import views
from .views import CompanyDetailFetchView, CompanyDetailView
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

urlpatterns = [
    path('', include(router.urls)),
    path('stock/<int:ticker>/', views.stock_price, name='stock-price'),
    path('companies/<str:code>/fetch-detail/',
         CompanyDetailFetchView.as_view(),
         name='company-fetch-detail'),
    path('companies/<str:code>/detail/',
         CompanyDetailView.as_view(),
         name='company-detail'),
]