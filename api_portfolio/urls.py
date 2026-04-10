# portfolio/urls.py
from django.urls import path
from .views import PortfolioListView, PortfolioDetailView

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
GET    /api/portfolio/        企業ごとに集計した一覧
POST   /api/portfolio/        銘柄追加（購入履歴1件）
GET    /api/portfolio/<id>/   購入履歴1件取得
PATCH  /api/portfolio/<id>/   購入履歴1件更新
DELETE /api/portfolio/<id>/   購入履歴1件削除
"""

urlpatterns = [
    path('',      PortfolioListView.as_view(),   name='portfolio-list'),
    path('<int:pk>/', PortfolioDetailView.as_view(), name='portfolio-detail'),
]
