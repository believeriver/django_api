#!/bin/bash
set -e

echo "=== Waiting for database... ==="
while ! python -c "
import django
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings_prod')
django.setup()
from django.db import connection
connection.ensure_connection()
" 2>/dev/null; do
    echo "Database not ready. Retrying in 2 seconds..."
    sleep 2
done

echo "=== Running migrations... ==="
# api_auth を先に migrate してから全体を migrate
python manage.py migrate api_auth --settings=config.settings_prod
python manage.py migrate --settings=config.settings_prod

echo "=== Collecting static files... ==="
python manage.py collectstatic --noinput --settings=config.settings_prod

echo "=== Starting gunicorn... ==="
gunicorn config.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 2 \
    --timeout 120 \
    --access-logfile /app/logs/gunicorn_access.log \
    --error-logfile /app/logs/gunicorn_error.log
