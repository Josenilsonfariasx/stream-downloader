#!/bin/bash
set -e

APP_PORT="${PORT:-8082}"

# Gerar SECRET_KEY se não existir
if [ -z "$SECRET_KEY" ]; then
    export SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")
fi

# Suporte opcional: cookies do YouTube via variável base64 (EasyPanel)
if [ -n "$YT_COOKIES_B64" ]; then
    mkdir -p /app/cookies
    echo "$YT_COOKIES_B64" | base64 -d > /app/cookies/youtube_cookies.txt
    export YT_COOKIES_FILE="${YT_COOKIES_FILE:-/app/cookies/youtube_cookies.txt}"
fi

# Renderizar porta do Nginx dinamicamente para EasyPanel/Fly
sed "s/__APP_PORT__/${APP_PORT}/g" /etc/nginx/nginx.conf > /etc/nginx/nginx.runtime.conf
mv /etc/nginx/nginx.runtime.conf /etc/nginx/nginx.conf

# Iniciar Nginx em background
nginx

# Iniciar Flask
cd /app
python -m gunicorn \
    --bind 0.0.0.0:5000 \
    --workers "${GUNICORN_WORKERS:-2}" \
    --threads "${GUNICORN_THREADS:-4}" \
    --timeout "${GUNICORN_TIMEOUT:-300}" \
    "app:create_app()"
