from django.urls import path
from .views import (
    WatchListView,
    WatchListDetailView,
    WatchItemView,
    WatchItemDetailView,
    WatchItemRefreshView,
)

"""
GET    /api/watchlist/                              リスト一覧（自分のみ）
POST   /api/watchlist/                              リスト作成
GET    /api/watchlist/<id>/                         リスト詳細（アイテム含む）
PATCH  /api/watchlist/<id>/                         リスト更新
DELETE /api/watchlist/<id>/                         リスト削除

GET    /api/watchlist/<id>/items/                   アイテム一覧
POST   /api/watchlist/<id>/items/                   アイテム追加
PATCH  /api/watchlist/<id>/items/<item_id>/         アイテム更新（手動入力含む）
DELETE /api/watchlist/<id>/items/<item_id>/         アイテム削除
POST   /api/watchlist/<id>/items/refresh/           株価自動更新・アラート判定
"""

urlpatterns = [
    path('',
         WatchListView.as_view(),
         name='watchlist-list'),
    path('<int:pk>/',
         WatchListDetailView.as_view(),
         name='watchlist-detail'),
    path('<int:watchlist_pk>/items/',
         WatchItemView.as_view(),
         name='watchitem-list'),
    path('<int:watchlist_pk>/items/<int:item_pk>/',
         WatchItemDetailView.as_view(),
         name='watchitem-detail'),
    path('<int:watchlist_pk>/items/refresh/',
         WatchItemRefreshView.as_view(),
         name='watchitem-refresh'),
]