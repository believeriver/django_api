# api_techlog/permissions.py
from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAuthorOrReadOnly(BasePermission):
    """
    参照は全員OK。
    更新・削除は作成者本人のみ許可。
    """
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:  # GET / HEAD / OPTIONS
            return True
        return obj.author == request.user
