from django.contrib import admin
from .models import WatchList, WatchItem


class WatchItemInline(admin.TabularInline):
    model         = WatchItem
    extra         = 0
    fields        = [
        'company', 'target_price', 'current_price',
        'alert_status', 'memo',
    ]
    readonly_fields = ['current_price', 'alert_status']


@admin.register(WatchList)
class WatchListAdmin(admin.ModelAdmin):
    list_display  = ['name', 'user', 'item_count', 'created_at']
    list_filter   = ['user']
    search_fields = ['name', 'user__email']
    inlines       = [WatchItemInline]

    def item_count(self, obj):
        return obj.items.count()
    item_count.short_description = '銘柄数'


@admin.register(WatchItem)
class WatchItemAdmin(admin.ModelAdmin):
    list_display  = [
        'watchlist', 'company', 'target_price',
        'current_price', 'alert_status',
    ]
    list_filter   = ['alert_status']
    search_fields = ['company__code', 'company__name']
    readonly_fields = ['alert_status']