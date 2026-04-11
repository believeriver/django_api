# api_techlog/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly, AllowAny
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import Category, Tag, Post, Like, Comment
from .serializers import (
    CategorySerializer,
    TagSerializer,
    PostListSerializer,
    PostDetailSerializer,
    CommentSerializer,
)
from .permissions import IsAuthorOrReadOnly


class CategoryListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        categories = Category.objects.all()
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data)


class TagListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        tags       = Tag.objects.all()
        serializer = TagSerializer(tags, many=True)
        return Response(serializer.data)


# api_techlog/views.py の PostListView のみ修正
class PostListView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request):
        """
        公開記事一覧（検索・フィルタリング対応）

        クエリパラメータ:
            [フィルタリング]
            category : カテゴリIDで絞り込み  例) ?category=1
            tag      : タグIDで絞り込み      例) ?tag=2
            author   : 著者IDで絞り込み      例) ?author=uuid
            search   : キーワード検索         例) ?search=Django
                       ※ タイトル・本文・タグ名を横断検索
                       ※ 複数条件は AND で絞り込み 例) ?category=1&search=Django

            [ソート]
            ordering=views   : 閲覧数の多い順
            ordering=likes   : いいね数の多い順
            ordering=created : 作成日順（デフォルト）

        """
        posts = Post.objects.filter(
            status='published'
        ).select_related(
            'author', 'category'
        ).prefetch_related('tags', 'likes', 'comments')

        # ── フィルタリング ──────────────────
        category_id = request.query_params.get('category')
        tag_id      = request.query_params.get('tag')
        author_id   = request.query_params.get('author')
        search      = request.query_params.get('search')

        if category_id:
            posts = posts.filter(category__id=category_id)

        if tag_id:
            posts = posts.filter(tags__id=tag_id)

        if author_id:
            posts = posts.filter(author__id=author_id)

        if search:
            # タイトル・本文・タグ名を横断検索
            from django.db.models import Q
            posts = posts.filter(
                Q(title__icontains=search)   |
                Q(content__icontains=search) |
                Q(tags__name__icontains=search)
            ).distinct()  # タグのJOINで重複が出るため distinct() が必要

        # ── ソート ──────────────────────────
        # ?ordering=views    → 閲覧数順
        # ?ordering=likes    → いいね数順
        # ?ordering=created  → 作成日順（デフォルト）
        ordering = request.query_params.get('ordering', 'created')
        if ordering == 'views':
            posts = posts.order_by('-views')
        elif ordering == 'likes':
            from django.db.models import Count
            posts = posts.annotate(
                likes_count=Count('likes')
            ).order_by('-likes_count')
        else:
            posts = posts.order_by('-created_at')

        serializer = PostListSerializer(posts, many=True)
        return Response(serializer.data)

    def post(self, request):
        """記事作成"""
        serializer = PostDetailSerializer(
            data=request.data,
            context={'request': request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class PostDetailView(APIView):
    # GETは全員OK、PATCH/DELETEは本人のみ
    permission_classes = [IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]

    def get_object(self, request, pk):
        post = get_object_or_404(
            Post.objects.select_related('author', 'category')
                        .prefetch_related('tags', 'likes', 'comments__author'),
            pk=pk,
        )
        # permission_classesのIsAuthorOrReadOnlyを実行
        self.check_object_permissions(request, post)
        return post

    def get(self, request, pk):
        post        = self.get_object(request, pk)
        post.views += 1
        post.save(update_fields=['views'])
        serializer  = PostDetailSerializer(post)
        return Response(serializer.data)

    def patch(self, request, pk):
        post       = self.get_object(request, pk)
        serializer = PostDetailSerializer(
            post,
            data=request.data,
            partial=True,
            context={'request': request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request, pk):
        post = self.get_object(request, pk)
        post.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class LikeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        post = get_object_or_404(Post, pk=pk)
        _, created = Like.objects.get_or_create(user=request.user, post=post)
        if not created:
            return Response(
                {'detail': 'Already liked.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response({'like_count': post.like_count}, status=status.HTTP_201_CREATED)

    def delete(self, request, pk):
        post = get_object_or_404(Post, pk=pk)
        like = Like.objects.filter(user=request.user, post=post).first()
        if not like:
            return Response(
                {'detail': 'Not liked yet.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        like.delete()
        return Response({'like_count': post.like_count}, status=status.HTTP_200_OK)


class CommentListView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request, pk):
        post       = get_object_or_404(Post, pk=pk)
        comments   = post.comments.select_related('author')
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)

    def post(self, request, pk):
        post       = get_object_or_404(Post, pk=pk)
        serializer = CommentSerializer(
            data=request.data,
            context={'request': request, 'post': post},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class CommentDetailView(APIView):
    # GETは全員OK、PATCH/DELETEは本人のみ
    permission_classes = [IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]

    def get_object(self, request, post_pk, comment_pk):
        comment = get_object_or_404(Comment, pk=comment_pk, post__pk=post_pk)
        # permission_classesのIsAuthorOrReadOnlyを実行
        self.check_object_permissions(request, comment)
        return comment

    def patch(self, request, pk, comment_pk):
        comment    = self.get_object(request, pk, comment_pk)
        serializer = CommentSerializer(
            comment,
            data=request.data,
            partial=True,
            context={'request': request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request, pk, comment_pk):
        comment = self.get_object(request, pk, comment_pk)
        comment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# api_techlog/views.py に追加
# api_techlog/views.py の MyPostListView を差し替え
class MyPostListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        自分の記事一覧（下書き含む）

        クエリパラメータ:
            [フィルタリング]
            status=draft     : 下書きのみ
            status=published : 公開済みのみ
            category         : カテゴリIDで絞り込み  例) ?category=1
            search           : キーワード検索         例) ?search=Django
                               ※ タイトル・本文を横断検索

            [ソート]
            ordering=views   : 閲覧数の多い順
            ordering=created : 作成日順（デフォルト）
        """
        posts = Post.objects.filter(
            author=request.user
        ).select_related(
            'author', 'category'
        ).prefetch_related('tags', 'likes', 'comments')

        # ── フィルタリング ──────────────────
        status_param = request.query_params.get('status')
        category_id  = request.query_params.get('category')
        search       = request.query_params.get('search')

        if status_param in ('draft', 'published'):
            posts = posts.filter(status=status_param)

        if category_id:
            posts = posts.filter(category__id=category_id)

        if search:
            from django.db.models import Q
            posts = posts.filter(
                Q(title__icontains=search) |
                Q(content__icontains=search)
            ).distinct()

        # ── ソート ──────────────────────────
        ordering = request.query_params.get('ordering', 'created')
        if ordering == 'views':
            posts = posts.order_by('-views')
        else:
            posts = posts.order_by('-created_at')

        serializer = PostListSerializer(posts, many=True)
        return Response(serializer.data)

