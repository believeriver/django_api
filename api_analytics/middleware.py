# api_analytics/middleware.py
import time
import json
import threading
from django.conf import settings
from django.utils.deprecation import MiddlewareMixin


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')


def get_site(path):
    if path.startswith('/api/blog/') or path.startswith('/blog/'):
        return 'blog'
    if path.startswith('/api/techlog/') or path.startswith('/techlog/'):
        return 'techlog'
    if path.startswith('/api/portfolio/') or path.startswith('/portfolio/'):
        return 'portfolio'
    if path.startswith('/api_market/') or path.startswith('/api/market/'):
        return 'market'
    return 'other'


def save_access_log(data: dict):
    """別スレッドでDBに保存（レスポンス速度に影響させない）"""
    def _save():
        try:
            from api_analytics.models import AccessLog
            AccessLog.objects.create(**data)
        except Exception as e:
            pass  # ログ保存失敗はサイレントに無視
    threading.Thread(target=_save, daemon=True).start()


def save_security_log(data: dict):
    """別スレッドでセキュリティログをDBに保存"""
    def _save():
        try:
            from api_analytics.models import SecurityLog
            SecurityLog.objects.create(**data)
        except Exception as e:
            pass
    threading.Thread(target=_save, daemon=True).start()


class AccessLogMiddleware(MiddlewareMixin):

    def process_request(self, request):
        request._start_time = time.time()

    def process_response(self, request, response):
        path = request.path

        # 除外パスはスキップ
        exclude_paths = getattr(settings, 'ANALYTICS_EXCLUDE_PATHS', [])
        if any(path.startswith(p) for p in exclude_paths):
            return response

        # レスポンスタイム計算
        start_time    = getattr(request, '_start_time', time.time())
        response_time = round((time.time() - start_time) * 1000, 2)

        ip         = get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        user       = request.user if request.user.is_authenticated else None

        # セキュリティパスの処理
        security_paths = getattr(settings, 'ANALYTICS_SECURITY_PATHS', [])
        if any(path.startswith(p) for p in security_paths):
            self._handle_security_log(
                request, response, path, ip, user, user_agent
            )
            return response

        # 通常アクセスログを保存
        save_access_log({
            'path':          path,
            'method':        request.method,
            'ip_address':    ip,
            'user':          user,
            'status_code':   response.status_code,
            'response_time': response_time,
            'user_agent':    user_agent,
            'site':          get_site(path),
        })

        return response

    def _handle_security_log(self, request, response,
                              path, ip, user, user_agent):
        """ログイン・ログアウトのセキュリティログを保存"""
        email  = ''
        action = ''

        if '/login/' in path:
            if response.status_code == 200:
                action = 'login_success'
                # レスポンスからemailを取得
                try:
                    body  = json.loads(response.content)
                    email = body.get('email', '')
                except Exception:
                    pass
            else:
                action = 'login_failed'
                # リクエストボディからemailを取得
                try:
                    body  = json.loads(request.body)
                    email = body.get('email', '')
                except Exception:
                    pass

        elif '/logout/' in path:
            action = 'logout'
            email  = user.email if user else ''

        if action:
            save_security_log({
                'action':     action,
                'ip_address': ip,
                'user':       user,
                'email':      email,
                'user_agent': user_agent,
            })
            