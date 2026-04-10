# portfolio/models.py
from django.db import models
from django.conf import settings


class Portfolio(models.Model):
    user           = models.ForeignKey(
                         settings.AUTH_USER_MODEL,
                         on_delete=models.CASCADE,
                         related_name='portfolios',
                     )
    company        = models.ForeignKey(
                         'api_market.Company',
                         on_delete=models.CASCADE,
                         related_name='portfolios',
                         to_field='code',
                     )
    shares         = models.PositiveIntegerField()
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2)
    purchased_at   = models.DateField()
    memo           = models.CharField(max_length=255, blank=True, default='')
    created_at     = models.DateTimeField(auto_now_add=True)
    updated_at     = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-purchased_at']

    def __str__(self):
        return f'{self.user} - {self.company_id} ({self.purchased_at})'
