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


class PostListView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request):
        posts      = Post.objects.filter(status='published').select_related(
                         'author', 'category'
                     ).prefetch_related('tags', 'likes', 'comments')
        serializer = PostListSerializer(posts, many=True)
        return Response(serializer.data)

    def post(self, request):
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
