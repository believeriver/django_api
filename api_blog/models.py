# api_blog/models.py
import uuid
import math
from django.db import models
from django.conf import settings
from django.utils import timezone


class Category(models.Model):
    name       = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Tag(models.Model):
    name       = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Post(models.Model):

    STATUS_CHOICES = [
        ('draft',     '下書き'),
        ('published', '公開'),
        ('archived',  '非公開'),
    ]

    id        = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    author    = models.ForeignKey(
                    settings.AUTH_USER_MODEL,
                    on_delete=models.CASCADE,
                    related_name='blog_posts',
                )
    title     = models.CharField(max_length=255)
    content   = models.TextField()                       # Markdown文字列
    summary   = models.TextField(blank=True, default='') # 一覧用の要約（任意）
    category  = models.ForeignKey(
                    Category,
                    on_delete=models.PROTECT,
                    related_name='posts',
                )
    tags      = models.ManyToManyField(
                    Tag,
                    blank=True,
                    related_name='posts',
                )
    thumbnail = models.ImageField(
                    upload_to='blog/thumbnails/%Y/%m/',  # 年月で整理
                    blank=True,
                    null=True,
                )
    location  = models.CharField(max_length=100, blank=True, default='')
    status    = models.CharField(
                    max_length=10,
                    choices=STATUS_CHOICES,
                    default='draft',
                )
    views      = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    @property
    def like_count(self):
        return self.likes.count()

    @property
    def comment_count(self):
        return self.comments.count()

    @property
    def reading_time(self):
        """
        読了時間を分単位で返す
        日本語: 500文字/分、英語: 200単語/分 を基準に計算
        負荷：文字数カウントのみ。DBアクセスなし。
        """
        if not self.content:
            return 1
        char_count = len(self.content)
        minutes    = math.ceil(char_count / 500)
        return max(1, minutes)  # 最低1分


class Like(models.Model):
    user       = models.ForeignKey(
                     settings.AUTH_USER_MODEL,
                     on_delete=models.CASCADE,
                     related_name='blog_likes',
                 )
    post       = models.ForeignKey(
                     Post,
                     on_delete=models.CASCADE,
                     related_name='likes',
                 )
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'post'],
                name='unique_blog_user_post_like',
            )
        ]

    def __str__(self):
        return f'{self.user} → {self.post.title[:20]}'


class Comment(models.Model):
    author     = models.ForeignKey(
                     settings.AUTH_USER_MODEL,
                     on_delete=models.CASCADE,
                     related_name='blog_comments',
                 )
    post       = models.ForeignKey(
                     Post,
                     on_delete=models.CASCADE,
                     related_name='comments',
                 )
    content    = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f'{self.author} → {self.post.title[:20]}'


class PostImage(models.Model):
    """本文中に埋め込む画像のアップロード"""
    post       = models.ForeignKey(
                     Post,
                     on_delete=models.CASCADE,
                     related_name='images',
                 )
    image      = models.ImageField(upload_to='blog/images/%Y/%m/')
    caption    = models.CharField(max_length=255, blank=True, default='')
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f'{self.post.title[:20]} - {self.image.name}'
