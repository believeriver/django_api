# api_blog/urls.py
from django.urls import path
from .views import (
    CategoryListView,
    TagListView,
    PostListView,
    PostDetailView,
    LikeView,
    CommentListView,
    CommentDetailView,
    PostImageUploadView,
)

"""
GET    /api/blog/categories/                         カテゴリ一覧
GET    /api/blog/tags/                               タグ一覧
GET    /api/blog/posts/                              公開記事一覧
POST   /api/blog/posts/                              記事作成（superuserのみ）
GET    /api/blog/posts/<uuid>/                       記事詳細
PATCH  /api/blog/posts/<uuid>/                       記事更新（superuserのみ）
DELETE /api/blog/posts/<uuid>/                       記事削除（superuserのみ）
POST   /api/blog/posts/<uuid>/like/                  いいね追加（要認証）
DELETE /api/blog/posts/<uuid>/like/                  いいね取消（要認証）
GET    /api/blog/posts/<uuid>/comments/              コメント一覧
POST   /api/blog/posts/<uuid>/comments/              コメント追加（要認証）
PATCH  /api/blog/posts/<uuid>/comments/<id>/         コメント更新（本人のみ）
DELETE /api/blog/posts/<uuid>/comments/<id>/         コメント削除（本人のみ）
POST   /api/blog/posts/<uuid>/images/                本文中画像アップロード（superuserのみ）
"""

urlpatterns = [
    path('categories/',                                    CategoryListView.as_view(),   name='blog-categories'),
    path('tags/',                                          TagListView.as_view(),        name='blog-tags'),
    path('posts/',                                         PostListView.as_view(),       name='blog-posts'),
    path('posts/<uuid:pk>/',                               PostDetailView.as_view(),     name='blog-post-detail'),
    path('posts/<uuid:pk>/like/',                          LikeView.as_view(),           name='blog-like'),
    path('posts/<uuid:pk>/comments/',                      CommentListView.as_view(),    name='blog-comments'),
    path('posts/<uuid:pk>/comments/<int:comment_pk>/',     CommentDetailView.as_view(),  name='blog-comment-detail'),
    path('posts/<uuid:pk>/images/',                        PostImageUploadView.as_view(), name='blog-image-upload'),
]
