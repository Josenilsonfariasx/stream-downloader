#!/bin/bash

# Gerar SECRET_KEY se não existir
if [ -z "$SECRET_KEY" ]; then
    export SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")
fi

# Iniciar Nginx em background
nginx

# Iniciar Flask
cd /app
python app.py
