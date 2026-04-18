# api_contact/views.py
from rest_framework import generics
from rest_framework.permissions import AllowAny, IsAdminUser
from django.core.mail import send_mail
from django.conf import settings
from .models import ContactMessage
from .serializers import ContactMessageCreateSerializer, ContactMessageSerializer

# メール通知のオンオフ（有効にする際は True に変更）
CONTACT_MAIL_ENABLED = False

"""
メール通知を有効にする際の手順（メモ）
# api_contact/views.py
CONTACT_MAIL_ENABLED = True  # ← Trueに変更

# settings.py（例：Gmailの場合）
EMAIL_BACKEND       = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST          = 'smtp.gmail.com'
EMAIL_PORT          = 587
EMAIL_USE_TLS       = True
EMAIL_HOST_USER     = 'your_gmail@gmail.com'
EMAIL_HOST_PASSWORD = 'your_app_password'  # Googleアプリパスワード
DEFAULT_FROM_EMAIL  = 'your_gmail@gmail.com'
ADMIN_EMAIL         = 'admin@example.com'
"""

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
