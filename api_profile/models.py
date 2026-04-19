# api_profile/models.py
from django.db import models


class Profile(models.Model):
    """基本プロフィール（1レコードのみ想定）"""
    name        = models.CharField(max_length=100)
    nickname    = models.CharField(max_length=100, blank=True, default='')
    location    = models.CharField(max_length=100, blank=True, default='')
    bio         = models.TextField(blank=True, default='')        # 自己紹介
    avatar      = models.ImageField(
                      upload_to='profile/',
                      blank=True,
                      null=True,
                  )                                                # 将来用
    is_active   = models.BooleanField(default=True)               # 公開フラグ
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return self.name


class Skill(models.Model):
    """スキル・資格・技術スタック"""

    CATEGORY_CHOICES = [
        ('certification', '資格'),
        ('language',      'プログラミング言語'),
        ('framework',     'フレームワーク'),
        ('infrastructure','インフラ'),
        ('network',       'ネットワーク'),
        ('tool',          'ツール'),
        ('other',         'その他'),
    ]

    profile     = models.ForeignKey(
                      Profile,
                      on_delete=models.CASCADE,
                      related_name='skills',
                  )
    category    = models.CharField(
                      max_length=20,
                      choices=CATEGORY_CHOICES,
                      default='other',
                  )
    name        = models.CharField(max_length=100)   # 例: CCNA / Python / Django
    level       = models.PositiveSmallIntegerField(
                      blank=True,
                      null=True,
                      help_text='習熟度 1〜5（任意）',
                  )
    description = models.CharField(max_length=255, blank=True, default='')
    order       = models.PositiveSmallIntegerField(default=0)  # 表示順

    class Meta:
        ordering = ['order', 'category', 'name']

    def __str__(self):
        return f'{self.name} ({self.category})'


class Career(models.Model):
    """業務経験"""
    profile     = models.ForeignKey(
                      Profile,
                      on_delete=models.CASCADE,
                      related_name='careers',
                  )
    company     = models.CharField(max_length=200, blank=True, default='')  # 任意
    title       = models.CharField(max_length=200)    # 役職・業務タイトル
    description = models.TextField(blank=True, default='')
    start_date  = models.DateField()
    end_date    = models.DateField(blank=True, null=True)  # nullは現職
    is_current  = models.BooleanField(default=False)       # 現職フラグ
    order       = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ['-start_date']

    def __str__(self):
        return f'{self.title} ({self.start_date} 〜)'


class Link(models.Model):
    """SNS・外部リンク"""

    PLATFORM_CHOICES = [
        ('github',   'GitHub'),
        ('twitter',  'Twitter / X'),
        ('linkedin', 'LinkedIn'),
        ('qiita',    'Qiita'),
        ('zenn',     'Zenn'),
        ('website',  'Webサイト'),
        ('other',    'その他'),
    ]

    profile   = models.ForeignKey(
                    Profile,
                    on_delete=models.CASCADE,
                    related_name='links',
                )
    platform  = models.CharField(
                    max_length=20,
                    choices=PLATFORM_CHOICES,
                    default='other',
                )
    url       = models.URLField()
    label     = models.CharField(max_length=100, blank=True, default='')
    order     = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ['order', 'platform']

    def __str__(self):
        return f'{self.platform}: {self.url}'
