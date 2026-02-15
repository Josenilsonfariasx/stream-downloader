#!/bin/bash
set -e

APP_PORT="${PORT:-8082}"

# Gerar SECRET_KEY se não existir
if [ -z "$SECRET_KEY" ]; then
    export SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")
fi

if [ -n "$YT_COOKIES_FILE" ]; then
    if [ -f "$YT_COOKIES_FILE" ]; then
        COOKIE_SIZE=$(wc -c < "$YT_COOKIES_FILE" | tr -d ' ')
        echo "[startup] YT_COOKIES_FILE encontrado em $YT_COOKIES_FILE (${COOKIE_SIZE} bytes)"
        if [ "$COOKIE_SIZE" -lt 200 ]; then
            echo "[startup] AVISO: arquivo de cookies parece pequeno demais e pode estar inválido"
        fi
    else
        echo "[startup] AVISO: YT_COOKIES_FILE configurado mas arquivo não existe: $YT_COOKIES_FILE"
    fi
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
