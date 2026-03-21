from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter

app_name = 'api_market'

router = DefaultRouter()
# router.register(r'companies', views.CompanyViewSet)

urlpatterns = [
    path('', include(router.urls)),

    # 追加: 株価取得 API
    # 例: /stock/7203/ または /stock/7203/?start=2025-01-01
    # path('stock/<int:ticker>/', views.stock_price, name='stock-price'),
]