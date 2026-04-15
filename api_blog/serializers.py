# api_blog/serializers.py
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Category, Tag, Post, Like, Comment, PostImage

User = get_user_model()


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model  = Category
        fields = ['id', 'name']


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Tag
        fields = ['id', 'name']


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model  = User
        fields = ['id', 'username']


class PostImageSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model  = PostImage
        fields = ['id', 'image_url', 'caption', 'created_at']

    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)
        return None


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
    """一覧用（content含まず）"""
    author        = AuthorSerializer(read_only=True)
    category      = CategorySerializer(read_only=True)
    tags          = TagSerializer(many=True, read_only=True)
    like_count    = serializers.IntegerField(read_only=True)
    comment_count = serializers.IntegerField(read_only=True)
    reading_time  = serializers.IntegerField(read_only=True)
    thumbnail_url = serializers.SerializerMethodField()

    class Meta:
        model  = Post
        fields = [
            'id', 'author', 'title', 'summary',
            'category', 'tags', 'thumbnail_url',
            'location', 'status', 'views',
            'like_count', 'comment_count', 'reading_time',
            'created_at', 'updated_at',
        ]

    def get_thumbnail_url(self, obj):
        request = self.context.get('request')
        if obj.thumbnail and request:
            return request.build_absolute_uri(obj.thumbnail.url)
        return None


class PostDetailSerializer(serializers.ModelSerializer):
    """詳細・作成・更新用（content含む）"""
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
    reading_time  = serializers.IntegerField(read_only=True)
    thumbnail_url = serializers.SerializerMethodField()
    comments      = CommentSerializer(many=True, read_only=True)
    images        = PostImageSerializer(many=True, read_only=True)

    class Meta:
        model  = Post
        fields = [
            'id', 'author', 'title', 'summary', 'content',
            'category', 'category_id',
            'tags', 'tag_ids',
            'thumbnail', 'thumbnail_url',
            'location', 'status', 'views',
            'like_count', 'comment_count', 'reading_time',
            'comments', 'images',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'author', 'views', 'updated_at']
        extra_kwargs = {
            'thumbnail': {'write_only': True},  # URLはthumbnail_urlで返す
        }

    def get_thumbnail_url(self, obj):
        request = self.context.get('request')
        if obj.thumbnail and request:
            return request.build_absolute_uri(obj.thumbnail.url)
        return None

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


class PostImageUploadSerializer(serializers.ModelSerializer):
    """本文中画像アップロード用"""
    image_url = serializers.SerializerMethodField()

    class Meta:
        model  = PostImage
        fields = ['id', 'image', 'image_url', 'caption']
        extra_kwargs = {'image': {'write_only': True}}

    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)
        return None
