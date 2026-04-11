# api_techlog/urls.py
from django.urls import path
from .views import (
    CategoryListView,
    TagListView,
    PostListView,
    PostDetailView,
    LikeView,
    CommentListView,
    CommentDetailView,
)

"""
URL patterns for the TechLog API.
GET    /api/techlog/categories/                    カテゴリ一覧
GET    /api/techlog/tags/                          タグ一覧
GET    /api/techlog/posts/                         記事一覧（公開済み）
POST   /api/techlog/posts/                         記事作成（要認証）
GET    /api/techlog/posts/<uuid>/                  記事詳細
PATCH  /api/techlog/posts/<uuid>/                  記事更新（本人のみ）
DELETE /api/techlog/posts/<uuid>/                  記事削除（本人のみ）
POST   /api/techlog/posts/<uuid>/like/             いいね追加（要認証）
DELETE /api/techlog/posts/<uuid>/like/             いいね取消（要認証）
GET    /api/techlog/posts/<uuid>/comments/         コメント一覧
POST   /api/techlog/posts/<uuid>/comments/         コメント追加（要認証）
PATCH  /api/techlog/posts/<uuid>/comments/<id>/    コメント更新（本人のみ）
DELETE /api/techlog/posts/<uuid>/comments/<id>/    コメント削除（本人のみ）

"""

urlpatterns = [
    path('categories/',                        CategoryListView.as_view(),  name='techlog-categories'),
    path('tags/',                              TagListView.as_view(),       name='techlog-tags'),
    path('posts/',                             PostListView.as_view(),      name='techlog-posts'),
    path('posts/<uuid:pk>/',                   PostDetailView.as_view(),    name='techlog-post-detail'),
    path('posts/<uuid:pk>/like/',              LikeView.as_view(),          name='techlog-like'),
    path('posts/<uuid:pk>/comments/',          CommentListView.as_view(),   name='techlog-comments'),
    path('posts/<uuid:pk>/comments/<int:comment_pk>/', CommentDetailView.as_view(), name='techlog-comment-detail'),
]
