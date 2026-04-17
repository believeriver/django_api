# api_analytics/models.py
from django.db import models
from django.conf import settings


class AccessLog(models.Model):

    SITE_CHOICES = [
        ('blog',      'Blog'),
        ('techlog',   'TechLog'),
        ('portfolio', 'Portfolio'),
        ('market',    'Market'),
        ('other',     'Other'),
    ]

    path          = models.CharField(max_length=512)
    method        = models.CharField(max_length=10)
    ip_address    = models.GenericIPAddressField(null=True, blank=True)
    user          = models.ForeignKey(
                        settings.AUTH_USER_MODEL,
                        on_delete=models.SET_NULL,
                        null=True, blank=True,
                        related_name='access_logs',
                    )
    status_code   = models.PositiveSmallIntegerField(null=True, blank=True)
    response_time = models.FloatField(null=True, blank=True, help_text='ms')
    user_agent    = models.TextField(blank=True, default='')
    site          = models.CharField(
                        max_length=20,
                        choices=SITE_CHOICES,
                        default='other',
                    )
    created_at    = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes  = [
            models.Index(fields=['created_at']),
            models.Index(fields=['site']),
            models.Index(fields=['ip_address']),
            models.Index(fields=['status_code']),
        ]

    def __str__(self):
        return f'{self.method} {self.path} [{self.status_code}] {self.created_at}'


class SecurityLog(models.Model):

    ACTION_CHOICES = [
        ('login_success', 'ログイン成功'),
        ('login_failed',  'ログイン失敗'),
        ('logout',        'ログアウト'),
    ]

    action      = models.CharField(max_length=20, choices=ACTION_CHOICES)
    ip_address  = models.GenericIPAddressField(null=True, blank=True)
    user        = models.ForeignKey(
                      settings.AUTH_USER_MODEL,
                      on_delete=models.SET_NULL,
                      null=True, blank=True,
                      related_name='security_logs',
                  )
    email       = models.EmailField(blank=True, default='')  # ログイン失敗時も記録
    user_agent  = models.TextField(blank=True, default='')
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes  = [
            models.Index(fields=['created_at']),
            models.Index(fields=['action']),
            models.Index(fields=['ip_address']),
        ]

    def __str__(self):
        return f'{self.action} {self.email} {self.created_at}'
