# api_blog/permissions.py
from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsSuperUserOrReadOnly(BasePermission):
    """
    参照は全員OK。
    作成・更新・削除は superuser のみ許可。
    """
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return request.user and request.user.is_superuser


class IsAuthorOrReadOnly(BasePermission):
    """
    コメントの更新・削除は本人のみ許可。
    """
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return obj.author == request.user
