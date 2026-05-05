# config/permissions.py
from rest_framework.permissions import IsAuthenticated


class IsSuperUser(IsAuthenticated):
    """
    superuserのみ許可
    用途: 企業詳細情報の取得（将来ユーザー公開の可能性あり）
    """
    def has_permission(self, request, view):
        return super().has_permission(request, view) and \
               request.user.is_superuser


class IsAuthenticatedUser(IsAuthenticated):
    """
    認証済みユーザー全員許可
    将来: 企業詳細情報の取得をユーザー公開する場合はこちらに切り替え
    """
    def has_permission(self, request, view):
        return super().has_permission(request, view)