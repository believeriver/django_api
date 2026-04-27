"""config URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('api_auth.urls')),
    path('api/market/', include('api_market.urls')),
    path('api/portfolio/', include('api_portfolio.urls')),
    path('api/techlog/', include('api_techlog.urls')),
    path('api/blog/', include('api_blog.urls')),
    path('api/analytics/', include('api_analytics.urls')),
    path('api/contact/', include('api_contact.urls')),
    path('api/profile/', include('api_profile.urls')),
    path('api/announce/', include('api_announce.urls')),
    path('api/watchlist/', include('api_watchlist.urls')),
]

urlpatterns += static(
    settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

