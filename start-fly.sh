#!/bin/bash
set -e

APP_PORT="${PORT:-8082}"

# Gerar SECRET_KEY se não existir
if [ -z "$SECRET_KEY" ]; then
    export SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")
fi

# Renderizar porta do Nginx dinamicamente para EasyPanel/Fly
sed "s/__APP_PORT__/${APP_PORT}/g" /etc/nginx/nginx.conf > /etc/nginx/nginx.runtime.conf
mv /etc/nginx/nginx.runtime.conf /etc/nginx/nginx.conf

# Iniciar Nginx em background
nginx

# Iniciar Flask
cd /app
python app.py
