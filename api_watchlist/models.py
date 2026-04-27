from django.db import models
from django.conf import settings
from api_market.models import Company


class WatchList(models.Model):

    user       = models.ForeignKey(
                     settings.AUTH_USER_MODEL,
                     on_delete=models.CASCADE,
                     related_name='watchlists',
                 )
    name       = models.CharField(max_length=100)
    memo       = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user.email} - {self.name}'


class WatchItem(models.Model):

    ALERT_NONE = 'none'
    ALERT_10   = 'alert_10'
    ALERT_20   = 'alert_20'

    ALERT_CHOICES = [
        (ALERT_NONE, 'なし'),
        (ALERT_10,   '10%以上下落'),
        (ALERT_20,   '20%以上下落'),
    ]

    watchlist     = models.ForeignKey(
                        WatchList,
                        on_delete=models.CASCADE,
                        related_name='items',
                    )
    company       = models.ForeignKey(
                        Company,
                        on_delete=models.CASCADE,
                        related_name='watch_items',
                    )
    target_price  = models.FloatField()
    current_price = models.FloatField(null=True, blank=True)
    memo          = models.TextField(blank=True, default='')
    alert_status  = models.CharField(
                        max_length=20,
                        choices=ALERT_CHOICES,
                        default=ALERT_NONE,
                    )
    created_at    = models.DateTimeField(auto_now_add=True)
    updated_at    = models.DateTimeField(auto_now=True)

    class Meta:
        ordering        = ['-created_at']
        unique_together = [['watchlist', 'company']]

    def __str__(self):
        return f'{self.watchlist.name} - {self.company.code}'

    @property
    def price_diff_pct(self):
        """目標株価からの差分（%）"""
        if self.current_price is None or self.target_price == 0:
            return None
        return round(
            ((self.current_price - self.target_price) / self.target_price) * 100,
            2,
        )

    def update_alert_status(self):
        """アラートフラグを更新"""
        pct = self.price_diff_pct
        if pct is None:
            self.alert_status = self.ALERT_NONE
        elif pct <= -20:
            self.alert_status = self.ALERT_20
        elif pct <= -10:
            self.alert_status = self.ALERT_10
        else:
            self.alert_status = self.ALERT_NONE
        self.save(update_fields=['alert_status', 'updated_at'])
