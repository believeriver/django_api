# api_announce/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db import models

from .models import Announcement, ChangeLog
from .serializers import AnnouncementSerializer, ChangeLogSerializer


class IsSuperUser(IsAuthenticated):
    """superuserのみ許可"""
    def has_permission(self, request, view):
        return super().has_permission(request, view) and \
               request.user.is_superuser


class AnnouncementListView(APIView):

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsSuperUser()]

    def get(self, request):
        """
        公開中のお知らせ一覧

        クエリパラメータ:
            type   : info / maintenance / feature / bugfix / warning
            all    : true の場合、管理者は全ステータスを取得可能
        """
        now = timezone.now()

        # 管理者かつ all=true の場合は全件取得
        if request.query_params.get('all') == 'true' and \
           request.user.is_authenticated and request.user.is_superuser:
            announcements = Announcement.objects.all()
        else:
            # 公開中・表示期間内のみ
            announcements = Announcement.objects.filter(
                status='published'
            ).filter(
                models.Q(start_at__isnull=True) | models.Q(start_at__lte=now)
            ).filter(
                models.Q(end_at__isnull=True) | models.Q(end_at__gte=now)
            )

        # タイプフィルタ
        type_param = request.query_params.get('type')
        if type_param:
            announcements = announcements.filter(type=type_param)

        serializer = AnnouncementSerializer(announcements, many=True)
        return Response(serializer.data)

    def post(self, request):
        """お知らせ作成（superuserのみ）"""
        serializer = AnnouncementSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class AnnouncementDetailView(APIView):

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsSuperUser()]

    def get_object(self, pk):
        return get_object_or_404(Announcement, pk=pk)

    def get(self, request, pk):
        """お知らせ詳細"""
        announcement = self.get_object(pk)
        serializer   = AnnouncementSerializer(announcement)
        return Response(serializer.data)

    def patch(self, request, pk):
        """お知らせ更新（superuserのみ）"""
        announcement = self.get_object(pk)
        serializer   = AnnouncementSerializer(
            announcement,
            data=request.data,
            partial=True,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request, pk):
        """お知らせ削除（superuserのみ）"""
        announcement = self.get_object(pk)
        announcement.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ChangeLogListView(APIView):

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsSuperUser()]

    def get(self, request):
        """
        変更履歴一覧

        クエリパラメータ:
            type    : feature / improve / bugfix / security / infra / breaking
            version : バージョンで絞り込み  例) ?version=v1.0.0
        """
        changelogs = ChangeLog.objects.all()

        type_param    = request.query_params.get('type')
        version_param = request.query_params.get('version')

        if type_param:
            changelogs = changelogs.filter(type=type_param)
        if version_param:
            changelogs = changelogs.filter(version=version_param)

        serializer = ChangeLogSerializer(changelogs, many=True)
        return Response(serializer.data)

    def post(self, request):
        """変更履歴作成（superuserのみ）"""
        serializer = ChangeLogSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ChangeLogDetailView(APIView):

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsSuperUser()]

    def get_object(self, pk):
        return get_object_or_404(ChangeLog, pk=pk)

    def get(self, request, pk):
        """変更履歴詳細"""
        changelog  = self.get_object(pk)
        serializer = ChangeLogSerializer(changelog)
        return Response(serializer.data)

    def patch(self, request, pk):
        """変更履歴更新（superuserのみ）"""
        changelog  = self.get_object(pk)
        serializer = ChangeLogSerializer(
            changelog,
            data=request.data,
            partial=True,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request, pk):
        """変更履歴削除（superuserのみ）"""
        changelog = self.get_object(pk)
        changelog.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
