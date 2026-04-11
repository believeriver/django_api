# api_techlog/serializers.py
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Category, Tag, Post, Like, Comment

User = get_user_model()


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model  = Category
        fields = ['id', 'name', 'created_at']


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Tag
        fields = ['id', 'name']


class AuthorSerializer(serializers.ModelSerializer):
    """記事・コメントに埋め込む著者情報"""
    class Meta:
        model  = User
        fields = ['id', 'username', 'email']


class CommentSerializer(serializers.ModelSerializer):
    author = AuthorSerializer(read_only=True)

    class Meta:
        model  = Comment
        fields = ['id', 'author', 'content', 'created_at', 'updated_at']
        read_only_fields = ['id', 'author', 'created_at', 'updated_at']

    def create(self, validated_data):
        validated_data['author'] = self.context['request'].user
        validated_data['post']   = self.context['post']
        return super().create(validated_data)


class PostListSerializer(serializers.ModelSerializer):
    """記事一覧用（contentは含めない）"""
    author        = AuthorSerializer(read_only=True)
    category      = CategorySerializer(read_only=True)
    tags          = TagSerializer(many=True, read_only=True)
    like_count    = serializers.IntegerField(read_only=True)
    comment_count = serializers.IntegerField(read_only=True)

    class Meta:
        model  = Post
        fields = [
            'id', 'author', 'title', 'category', 'tags',
            'status', 'views', 'like_count', 'comment_count',
            'created_at', 'updated_at',
        ]


class PostDetailSerializer(serializers.ModelSerializer):
    """記事詳細・作成・更新用（contentを含む）"""
    author        = AuthorSerializer(read_only=True)
    category      = CategorySerializer(read_only=True)
    category_id   = serializers.PrimaryKeyRelatedField(
                        queryset=Category.objects.all(),
                        source='category',
                        write_only=True,
                    )
    tags          = TagSerializer(many=True, read_only=True)
    tag_ids       = serializers.PrimaryKeyRelatedField(
                        queryset=Tag.objects.all(),
                        source='tags',
                        many=True,
                        write_only=True,
                        required=False,
                    )
    like_count    = serializers.IntegerField(read_only=True)
    comment_count = serializers.IntegerField(read_only=True)
    comments      = CommentSerializer(many=True, read_only=True)

    class Meta:
        model  = Post
        fields = [
            'id', 'author', 'title', 'content',
            'category', 'category_id',
            'tags', 'tag_ids',
            'status', 'views', 'like_count', 'comment_count',
            'comments', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'author', 'views', 'created_at', 'updated_at']

    def create(self, validated_data):
        tags = validated_data.pop('tags', [])
        validated_data['author'] = self.context['request'].user
        post = super().create(validated_data)
        post.tags.set(tags)
        return post

    def update(self, instance, validated_data):
        tags = validated_data.pop('tags', None)
        post = super().update(instance, validated_data)
        if tags is not None:
            post.tags.set(tags)
        return post
