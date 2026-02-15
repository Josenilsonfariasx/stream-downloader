# Guia de Deploy

## Opção 1: Railway (Mais Fácil)

1. Instale o Railway CLI:

```bash
npm i -g @railway/cli
```

2. Login e deploy:

```bash
railway login
railway init
railway up
```

3. Configure as variáveis de ambiente no dashboard Railway
4. Pronto! Você terá uma URL como: `seu-app.railway.app`

---

## Opção 2: Render.com

1. Crie conta em render.com
2. Conecte seu repositório GitHub
3. Crie "New Web Service"
4. Selecione Docker
5. Configure as variáveis de ambiente
6. Deploy automático!

---

## Opção 3: VPS (DigitalOcean, AWS, etc.)

### 1. Preparação

Crie uma SECRET_KEY segura:

```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

Edite `.env.production` e coloque a SECRET_KEY gerada.

### 2. No servidor VPS:

#### Instalar Docker e Docker Compose:

```bash
# Atualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Instalar Docker Compose
sudo apt install docker-compose-plugin -y

# Adicionar usuário ao grupo docker
sudo usermod -aG docker $USER
newgrp docker
```

#### Clonar seu projeto:

```bash
git clone seu-repositorio.git
cd stream2downloader
```

#### Configurar ambiente:

```bash
# Copiar arquivo de produção
cp .env.production .env

# Editar e adicionar SECRET_KEY
nano .env
```

#### SSL/HTTPS com Certbot (Opcional mas recomendado):

```bash
# Criar diretório SSL temporário
mkdir -p ssl
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout ssl/key.pem -out ssl/cert.pem

# Para SSL real (depois):
sudo apt install certbot
# Siga instruções do Certbot para seu domínio
```

#### Iniciar aplicação:

```bash
# Produção
docker compose -f docker-compose.prod.yml up -d

# Ver logs
docker compose -f docker-compose.prod.yml logs -f

# Parar
docker compose -f docker-compose.prod.yml down
```

### 3. Configurar Firewall:

```bash
# Permitir portas HTTP/HTTPS configuradas para o frontend
sudo ufw allow 8081/tcp
sudo ufw allow 8443/tcp
sudo ufw allow 22/tcp  # SSH
sudo ufw enable
```

### 4. Configurar Domínio:

No painel do seu domínio (GoDaddy, Namecheap, etc.):

- Crie um registro A apontando para o IP do seu VPS
- Exemplo: `downloader.seudominio.com` → `IP_DO_VPS`

### 5. SSL Gratuito com Certbot:

```bash
sudo certbot certonly --standalone -d seudominio.com
sudo cp /etc/letsencrypt/live/seudominio.com/fullchain.pem ssl/cert.pem
sudo cp /etc/letsencrypt/live/seudominio.com/privkey.pem ssl/key.pem
docker compose -f docker-compose.prod.yml restart frontend
```

---

## Opção 4: Fly.io

1. Instale Fly CLI:

```bash
curl -L https://fly.io/install.sh | sh
```

2. Login e deploy:

```bash
fly auth login
fly launch
fly deploy
```

---

## Monitoramento

### Ver logs em tempo real:

```bash
docker compose -f docker-compose.prod.yml logs -f
```

### Verificar status:

```bash
docker compose -f docker-compose.prod.yml ps
```

### Reiniciar serviços:

```bash
docker compose -f docker-compose.prod.yml restart
```

### Atualizar aplicação:

```bash
git pull
docker compose -f docker-compose.prod.yml down
docker compose -f docker-compose.prod.yml up -d --build
```

---

## Segurança

1. ✅ Sempre use HTTPS em produção
2. ✅ Configure SECRET_KEY única
3. ✅ Use rate limiting (já configurado no nginx)
4. ✅ Configure firewall no servidor
5. ✅ Mantenha Docker e sistema atualizados
6. ✅ Faça backups regulares

---

## Custos Estimados

- **Railway**: Grátis (limitado) → $5-10/mês
- **Render**: Grátis (limitado) → $7/mês
- **Fly.io**: Grátis (3 apps) → $5/mês
- **DigitalOcean VPS**: $6/mês (básico)
- **AWS EC2**: $3-15/mês (depende do uso)

---

## Suporte

Problemas comuns:

### Erro 502 Bad Gateway

```bash
docker compose -f docker-compose.prod.yml restart backend
```

### Download lento

- Verifique recursos do servidor (CPU/RAM)
- Considere upgrade de plano

### Erro de SSL

- Verifique certificados em `/ssl`
- Renove com Certbot se necessário
