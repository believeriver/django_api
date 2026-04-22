# django_api/Dockerfile
FROM python:3.9-slim

# 作業ディレクトリ
WORKDIR /app

# システムパッケージ
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Pythonパッケージ
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# アプリコード
COPY . .

# ログディレクトリ作成
RUN mkdir -p /app/logs

# 静的ファイル収集・マイグレーション・起動スクリプト
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["/entrypoint.sh"]
