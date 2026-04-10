# portfolio/urls.py
from django.urls import path
from .views import (
    PortfolioListView,
    PortfolioDetailView,
    PortfolioDashboardView,
    PortfolioIndustryView,
)

"""
# 認証
POST   /api/auth/register/
POST   /api/auth/login/
POST   /api/auth/refresh/
POST   /api/auth/logout/
POST   /api/auth/change-password/
GET    /api/auth/profile/
PATCH  /api/auth/profile/
DELETE /api/auth/profile/

# ポートフォリオ
GET    /api/portfolio/        企業ごとに集計した一覧(購入履歴一覧（集計）)
POST   /api/portfolio/        銘柄追加（購入履歴1件）
GET    /api/portfolio/<id>/   購入履歴1件取得
PATCH  /api/portfolio/<id>/   購入履歴1件更新
DELETE /api/portfolio/<id>/   購入履歴1件削除
GET  /api/portfolio/dashboard/  ダッシュボード用（業種・指標込み）
GET  /api/portfolio/industry/   業種別集計（円グラフ用）
"""

urlpatterns = [
    path('',      PortfolioListView.as_view(),   name='portfolio-list'),
    path('<int:pk>/', PortfolioDetailView.as_view(), name='portfolio-detail'),
    path('dashboard/', PortfolioDashboardView.as_view(), name='portfolio-dashboard'),
    path('industry/', PortfolioIndustryView.as_view(), name='portfolio-industry'),
]
