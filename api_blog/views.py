# api_blog/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly, AllowAny
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.shortcuts import get_object_or_404
from django.db.models import Q

from .models import Category, Tag, Post, Like, Comment, PostImage
from .serializers import (
    CategorySerializer,
    TagSerializer,
    PostListSerializer,
    PostDetailSerializer,
    CommentSerializer,
    PostImageUploadSerializer,
)
from .permissions import IsSuperUserOrReadOnly, IsAuthorOrReadOnly


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


class PostListView(APIView):
    permission_classes = [IsSuperUserOrReadOnly]
    parser_classes     = [MultiPartParser, FormParser, JSONParser]

    def get(self, request):
        """
        公開記事一覧（検索・フィルタリング対応）

        クエリパラメータ:
            [フィルタリング]
            category : カテゴリIDで絞り込み  例) ?category=1
            tag      : タグIDで絞り込み      例) ?tag=2
            search   : キーワード検索         例) ?search=朝活
                       ※ タイトル・要約・本文を横断検索

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

        category_id = request.query_params.get('category')
        tag_id      = request.query_params.get('tag')
        search      = request.query_params.get('search')

        if category_id:
            posts = posts.filter(category__id=category_id)

        if tag_id:
            posts = posts.filter(tags__id=tag_id)

        if search:
            posts = posts.filter(
                Q(title__icontains=search)   |
                Q(summary__icontains=search) |
                Q(content__icontains=search)
            ).distinct()

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

        serializer = PostListSerializer(posts, many=True, context={'request': request})
        return Response(serializer.data)

    def post(self, request):
        """記事作成（superuserのみ）"""
        serializer = PostDetailSerializer(
            data=request.data,
            context={'request': request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class PostDetailView(APIView):
    permission_classes = [IsSuperUserOrReadOnly]
    parser_classes     = [MultiPartParser, FormParser, JSONParser]

    def get_object(self, request, pk):
        post = get_object_or_404(
            Post.objects.select_related('author', 'category')
                        .prefetch_related('tags', 'likes', 'comments__author', 'images'),
            pk=pk,
        )
        self.check_object_permissions(request, post)
        return post

    def get(self, request, pk):
        """記事詳細（閲覧数カウントアップ）"""
        post        = self.get_object(request, pk)
        post.views += 1
        post.save(update_fields=['views'])
        serializer  = PostDetailSerializer(post, context={'request': request})
        return Response(serializer.data)

    def patch(self, request, pk):
        """記事更新（superuserのみ）"""
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
        """記事削除（superuserのみ）"""
        post = self.get_object(request, pk)
        post.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class LikeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        """いいね追加"""
        post       = get_object_or_404(Post, pk=pk, status='published')
        _, created = Like.objects.get_or_create(user=request.user, post=post)
        if not created:
            return Response(
                {'detail': 'Already liked.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response({'like_count': post.like_count}, status=status.HTTP_201_CREATED)

    def delete(self, request, pk):
        """いいね取消"""
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
        """コメント一覧"""
        post       = get_object_or_404(Post, pk=pk, status='published')
        comments   = post.comments.select_related('author')
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)

    def post(self, request, pk):
        """コメント追加（認証ユーザーのみ）"""
        post       = get_object_or_404(Post, pk=pk, status='published')
        serializer = CommentSerializer(
            data=request.data,
            context={'request': request, 'post': post},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class CommentDetailView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]

    def get_object(self, request, post_pk, comment_pk):
        comment = get_object_or_404(Comment, pk=comment_pk, post__pk=post_pk)
        self.check_object_permissions(request, comment)
        return comment

    def patch(self, request, pk, comment_pk):
        """コメント更新（本人のみ）"""
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
        """コメント削除（本人のみ）"""
        comment = self.get_object(request, pk, comment_pk)
        comment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class PostImageUploadView(APIView):
    """本文中画像アップロード（superuserのみ）"""
    permission_classes = [IsAuthenticated]
    parser_classes     = [MultiPartParser, FormParser]

    def post(self, request, pk):
        post       = get_object_or_404(Post, pk=pk)
        if not request.user.is_superuser:
            return Response(
                {'detail': 'Permission denied.'},
                status=status.HTTP_403_FORBIDDEN,
            )
        serializer = PostImageUploadSerializer(
            data=request.data,
            context={'request': request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save(post=post)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
