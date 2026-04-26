# api_announce/urls.py
from django.urls import path
from .views import (
    AnnouncementListView,
    AnnouncementDetailView,
    ChangeLogListView,
    ChangeLogDetailView,
)

"""
GET    /api/announce/                公開中のお知らせ一覧（認証不要）
GET    /api/announce/?all=true       全件取得（superuserのみ有効）
GET    /api/announce/?type=maintenance タイプ絞り込み
POST   /api/announce/                作成（superuserのみ）
GET    /api/announce/<id>/           詳細（認証不要）
PATCH  /api/announce/<id>/           更新（superuserのみ）
DELETE /api/announce/<id>/           削除（superuserのみ）

GET    /api/announce/changelog/              変更履歴一覧（認証不要）
GET    /api/announce/changelog/?type=feature タイプ絞り込み
GET    /api/announce/changelog/?version=v1.0.0 バージョン絞り込み
POST   /api/announce/changelog/              作成（superuserのみ）
GET    /api/announce/changelog/<id>/         詳細（認証不要）
PATCH  /api/announce/changelog/<id>/         更新（superuserのみ）
DELETE /api/announce/changelog/<id>/         削除（superuserのみ）
"""

urlpatterns = [
    path('',                    AnnouncementListView.as_view(),  name='announce-list'),
    path('<int:pk>/',           AnnouncementDetailView.as_view(), name='announce-detail'),
    path('changelog/',          ChangeLogListView.as_view(),     name='changelog-list'),
    path('changelog/<int:pk>/', ChangeLogDetailView.as_view(),   name='changelog-detail'),
]
