# api_techlog/models.py
import uuid
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
    ]

    id       = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    author   = models.ForeignKey(
                   settings.AUTH_USER_MODEL,
                   on_delete=models.CASCADE,
                   related_name='techlog_posts',
               )
    title    = models.CharField(max_length=255)
    content  = models.TextField()               # Markdown文字列として保存
    category = models.ForeignKey(
                   Category,
                   on_delete=models.PROTECT,
                   related_name='posts',
               )
    tags     = models.ManyToManyField(
                   Tag,
                   blank=True,
                   related_name='posts',
               )
    status   = models.CharField(
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


class Like(models.Model):
    """いいね（ユーザーと記事の中間テーブル）"""
    user       = models.ForeignKey(
                     settings.AUTH_USER_MODEL,
                     on_delete=models.CASCADE,
                     related_name='techlog_likes',
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
                name='unique_user_post_like',
            )
        ]

    def __str__(self):
        return f'{self.user} → {self.post.title[:20]}'


class Comment(models.Model):
    author     = models.ForeignKey(
                     settings.AUTH_USER_MODEL,
                     on_delete=models.CASCADE,
                     related_name='techlog_comments',
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
