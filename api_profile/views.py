# api_profile/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import Profile
from .serializers import ProfileSerializer


class ProfileView(APIView):
    """
    GET /api/profile/   → 公開プロフィール取得（認証不要）
    """
    permission_classes = [AllowAny]

    def get(self, request):
        # is_active=True の最新1件を返す
        profile = Profile.objects.filter(
            is_active=True
        ).prefetch_related(
            'skills', 'careers', 'links'
        ).first()

        if not profile:
            return Response(
                {'detail': 'Profile not found.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = ProfileSerializer(
            profile,
            context={'request': request},
        )
        return Response(serializer.data)