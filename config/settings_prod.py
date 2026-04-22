# config/settings_prod.py
from .settings import *
import environ

# 本番用の環境変数を読み込む
env = environ.Env()
root = environ.Path(BASE_DIR / 'secrets')
env.read_env(root('.env.prod'))  # ← .env.prod を読み込む

# セキュリティ設定
DEBUG      = env.bool('DEBUG', default=False)
SECRET_KEY = env.str('SECRET_KEY')
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS')

# データベース（PostgreSQL）
DATABASES = {
    'default': {
        'ENGINE':   'django.db.backends.postgresql',
        'NAME':     env.str('DB_NAME'),
        'USER':     env.str('DB_USER'),
        'PASSWORD': env.str('DB_PASSWORD'),
        'HOST':     env.str('DB_HOST', default='db'),
        'PORT':     env.str('DB_PORT', default='5432'),
    }
}

# 静的ファイル
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# CORS（本番は特定ドメインのみ許可）
CORS_ORIGIN_ALLOW_ALL = False
CORS_ALLOWED_ORIGINS = [
    'https://www.believeriver.site',
]

# セキュリティ
SECURE_SSL_REDIRECT          = True
SESSION_COOKIE_SECURE        = True
CSRF_COOKIE_SECURE           = True
SECURE_BROWSER_XSS_FILTER    = True
SECURE_CONTENT_TYPE_NOSNIFF  = True
SECURE_HSTS_SECONDS          = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True

# キャッシュ（本番はRedis）
CACHES = {
    'default': {
        'BACKEND':  'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'api_market_cache',
    }
}

# ログ（本番はファイル出力）
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s'
        },
    },
    'handlers': {
        'file': {
            'level':    'WARNING',
            'class':    'logging.FileHandler',
            'filename': '/app/logs/django.log',
            'formatter': 'standard',
        },
        'console': {
            'level':    'INFO',
            'class':    'logging.StreamHandler',
            'formatter': 'standard',
        },
    },
    'loggers': {
        'django': {
            'handlers':  ['file', 'console'],
            'level':     'WARNING',
            'propagate': False,
        },
        'api_market': {
            'handlers':  ['file', 'console'],
            'level':     'WARNING',
            'propagate': False,
        },
    }
}

# メール設定
DEFAULT_FROM_EMAIL = env.str('DEFAULT_FROM_EMAIL', default='noreply@believeriver.site')
ADMIN_EMAIL        = env.str('ADMIN_EMAIL', default='')
