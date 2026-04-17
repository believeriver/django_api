# api_analytics/urls.py
from django.urls import path
from .views import (
    SummaryView,
    AccessLogListView,
    SecurityLogListView,
    PopularPagesView,
    DailyAccessView,
    SiteAccessView,
    ExportCSVView,
)

urlpatterns = [
    path('summary/',       SummaryView.as_view(),         name='analytics-summary'),
    path('access-logs/',   AccessLogListView.as_view(),    name='analytics-access-logs'),
    path('security-logs/', SecurityLogListView.as_view(),  name='analytics-security-logs'),
    path('popular-pages/', PopularPagesView.as_view(),     name='analytics-popular-pages'),
    path('daily/',         DailyAccessView.as_view(),      name='analytics-daily'),
    path('sites/',         SiteAccessView.as_view(),       name='analytics-sites'),
    path('export/',        ExportCSVView.as_view(),        name='analytics-export'),
]
