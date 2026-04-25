# api_announce/models.py
from django.db import models
from django.utils import timezone


class Announcement(models.Model):

    TYPE_CHOICES = [
        ('info',        'お知らせ'),
        ('maintenance', 'メンテナンス'),
        ('feature',     '新機能'),
        ('bugfix',      'バグ修正'),
        ('warning',     '警告'),
    ]

    STATUS_CHOICES = [
        ('draft',     '下書き'),
        ('published', '公開'),
        ('archived',  '終了'),
    ]

    title     = models.CharField(max_length=255)
    content   = models.TextField(blank=True, default='')
    type      = models.CharField(
                    max_length=20,
                    choices=TYPE_CHOICES,
                    default='info',
                )
    status    = models.CharField(
                    max_length=20,
                    choices=STATUS_CHOICES,
                    default='draft',
                )
    is_pinned = models.BooleanField(default=False)
    start_at  = models.DateTimeField(null=True, blank=True)
    end_at    = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-is_pinned', '-created_at']

    def __str__(self):
        return self.title

    @property
    def is_active(self):
        """表示期間内かどうかを判定"""
        now = timezone.now()
        if self.status != 'published':
            return False
        if self.start_at and now < self.start_at:
            return False
        if self.end_at and now > self.end_at:
            return False
        return True


class ChangeLog(models.Model):

    TYPE_CHOICES = [
        ('feature',  '機能追加'),
        ('improve',  '改善'),
        ('bugfix',   'バグ修正'),
        ('security', 'セキュリティ'),
        ('infra',    'インフラ'),
        ('breaking', '破壊的変更'),
    ]

    version     = models.CharField(max_length=20)
    type        = models.CharField(
                      max_length=20,
                      choices=TYPE_CHOICES,
                      default='feature',
                  )
    title       = models.CharField(max_length=255)
    content     = models.TextField(blank=True, default='')
    released_at = models.DateTimeField(default=timezone.now)
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-released_at']

    def __str__(self):
        return f'{self.version} - {self.title}'
