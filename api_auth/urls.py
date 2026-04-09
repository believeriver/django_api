from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    RegisterView,
    CustomTokenObtainPairView,
    LogoutView,
    ChangePasswordView,
    ProfileUpdateView,
)

"""
POST   /api/auth/register/        ユーザー登録
POST   /api/auth/login/           ログイン（JWT取得）
POST   /api/auth/refresh/         トークンリフレッシュ
POST   /api/auth/logout/          ログアウト（Blacklist登録）
POST   /api/auth/change-password/ パスワード変更
GET    /api/auth/profile/         プロフィール取得
PATCH  /api/auth/profile/         プロフィール更新
"""

urlpatterns = [
    path('register/', RegisterView.as_view(),              name='auth-register'),
    path('login/',    CustomTokenObtainPairView.as_view(), name='auth-login'),
    path('refresh/',  TokenRefreshView.as_view(),          name='auth-refresh'),
    path('logout/',   LogoutView.as_view(),                name='auth-logout'),
    path('change-password/', ChangePasswordView.as_view(), name='auth-change-password'),
    path('profile/', ProfileUpdateView.as_view(), name='auth-profile'),
]
