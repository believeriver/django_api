# api_contact/views.py
from rest_framework import generics
from rest_framework.permissions import AllowAny, IsAdminUser
from django.core.mail import send_mail
from django.conf import settings
from .models import ContactMessage
from .serializers import ContactMessageCreateSerializer, ContactMessageSerializer

# メール通知のオンオフ（有効にする際は True に変更）
CONTACT_MAIL_ENABLED = False


class ContactCreateView(generics.CreateAPIView):
    """POST /api/contact/ — 誰でも送信可"""
    permission_classes = [AllowAny]
    serializer_class   = ContactMessageCreateSerializer

    def perform_create(self, serializer):
        instance = serializer.save()
        if CONTACT_MAIL_ENABLED:
            send_mail(
                subject=f'[お問い合わせ] {instance.subject}',
                message=f'{instance.name}\n{instance.email}\n\n{instance.body}',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[settings.ADMIN_EMAIL],
                fail_silently=True,
            )


class ContactListView(generics.ListAPIView):
    """GET /api/contact/list/ — 管理者のみ"""
    permission_classes = [IsAdminUser]
    serializer_class   = ContactMessageSerializer
    queryset           = ContactMessage.objects.all()


class ContactDetailView(generics.RetrieveUpdateDestroyAPIView):
    """GET/PATCH/DELETE /api/contact/<id>/ — 管理者のみ（既読更新・削除）"""
    permission_classes = [IsAdminUser]
    serializer_class   = ContactMessageSerializer
    queryset           = ContactMessage.objects.all()
