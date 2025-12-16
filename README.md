# 📺 YouTube Downloader

Sistema web para download de vídeos do YouTube com preview e seleção de qualidade.

## 🚀 Tecnologias

- **Backend**: Python 3.8+ com Flask
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **Download**: yt-dlp
- **Infraestrutura**: Docker (opcional)

## 📋 Funcionalidades

✅ Validação de URLs do YouTube  
✅ Preview com miniatura, título e duração  
✅ Seleção de qualidade de vídeo  
✅ Download direto no navegador  
✅ Interface responsiva e moderna  
✅ Limpeza automática de arquivos temporários

## 🛠️ Instalação

### 🐳 Com Docker (Recomendado)

**Pré-requisitos:**

- Docker
- Docker Compose

**Instalação em 2 passos:**

1. **Clone o repositório**

```bash
git clone https://github.com/seu-usuario/stream-downloader.git
cd stream-downloader
```

2. **Inicie os containers**

```bash
docker-compose up -d
```

Pronto! Acesse: **http://localhost:8080** 🎉

**Comandos úteis:**

```bash
# Ver logs
docker-compose logs -f

# Parar containers
docker-compose down

# Rebuild após alterações
docker-compose up -d --build

# Ver status
docker-compose ps
```

---

### 💻 Instalação Manual (Sem Docker)

**Pré-requisitos:**

- Python 3.8 ou superior
- pip (gerenciador de pacotes Python)

**Passo a Passo:**

1. **Clone o repositório**

```bash
git clone https://github.com/seu-usuario/stream-downloader.git
cd stream-downloader
```

2. **Configure o ambiente virtual Python**

```bash
cd backend
python -m venv venv

# Linux/Mac
source venv/bin/activate

# Windows
venv\Scripts\activate
```

3. **Instale as dependências**

```bash
pip install -r requirements.txt
```

4. **Configure as variáveis de ambiente (opcional)**

```bash
cp .env.example .env
# Edite o arquivo .env com suas configurações
```

5. **Inicie o servidor**

```bash
python app.py
```

O servidor estará rodando em `http://localhost:5000`

6. **Abra o frontend**

Abra o arquivo `frontend/index.html` no navegador ou use um servidor local:

```bash
# Com Python
cd ../frontend
python -m http.server 8000

# Acesse: http://localhost:8000
```

## 📁 Estrutura do Projeto

```
stream-downloader/
├── backend/
│   ├── app.py                 # Aplicação Flask principal
│   ├── config.py              # Configurações
│   ├── requirements.txt       # Dependências Python
│   ├── .env.example          # Exemplo de variáveis de ambiente
│   ├── routes/
│   │   ├── __init__.py
│   │   └── download.py       # Rotas da API
│   ├── services/
│   │   ├── __init__.py
│   │   └── youtube_service.py # Lógica de download
│   └── utils/
│       ├── __init__.py
│       └── validators.py      # Validações
├── frontend/
│   ├── index.html            # Interface principal
│   ├── css/
│   │   └── style.css         # Estilos
│   └── js/
│       └── app.js            # Lógica do frontend
├── downloads/                # Arquivos temporários
├── docs/                     # Documentação
├── .gitignore
└── README.md
```

## 🔌 API Endpoints

### `POST /api/validate`

Valida URL e retorna informações do vídeo.

**Request:**

```json
{
  "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
}
```

**Response:**

```json
{
  "success": true,
  "data": {
    "video_id": "dQw4w9WgXcQ",
    "title": "Rick Astley - Never Gonna Give You Up",
    "thumbnail": "https://...",
    "duration": 212,
    "duration_string": "3:32",
    "uploader": "Rick Astley",
    "qualities": [
      {
        "value": "best",
        "label": "Melhor qualidade"
      },
      {
        "value": "1080p",
        "label": "1080p"
      }
    ]
  }
}
```

### `POST /api/download`

Faz download do vídeo.

**Request:**

```json
{
  "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
  "quality": "720p"
}
```

**Response:** Stream do arquivo de vídeo

### `GET /api/health`

Health check da API.

**Response:**

```json
{
  "status": "healthy",
  "service": "youtube-downloader"
}
```

## ⚙️ Configurações

### Com Docker

As configurações são definidas no [docker-compose.yml](docker-compose.yml):

```yaml
environment:
  - DEBUG=True
  - SECRET_KEY=change-this-in-production
  - CORS_ORIGINS=*
  - MAX_VIDEO_DURATION=3600 # segundos (1 hora)
  - MAX_FILE_SIZE=524288000 # bytes (500MB)
  - TEMP_FILE_RETENTION=3600 # segundos (1 hora)
```

### Instalação Manual

As configurações podem ser ajustadas no arquivo `.env`:

```env
# Desenvolvimento
DEBUG=True

# Segurança
SECRET_KEY=your-secret-key-here

# CORS
CORS_ORIGINS=*

# Limites
MAX_VIDEO_DURATION=3600        # segundos (1 hora)
MAX_FILE_SIZE=524288000        # bytes (500MB)

# Limpeza
TEMP_FILE_RETENTION=3600       # segundos (1 hora)

# Rate Limiting
RATE_LIMIT_ENABLED=False
RATE_LIMIT_PER_MINUTE=10
```

## 🚢 Deploy em Produção

### Docker Compose (Produção)

1. Edite o `docker-compose.yml` e configure:

   - `DEBUG=False`
   - `SECRET_KEY` seguro (gere com `python -c "import secrets; print(secrets.token_hex(32))"`)
   - `CORS_ORIGINS` específico (ex: `https://seudominio.com`)

2. Execute:

```bash
docker-compose up -d
```

3. Configure um reverse proxy (nginx/traefik) com SSL para produção.

### Docker Hub

```bash
# Build e push
docker build -t seu-usuario/youtube-downloader:latest ./backend
docker push seu-usuario/youtube-downloader:latest

# Pull e run em produção
docker pull seu-usuario/youtube-downloader:latest
docker run -d -p 5000:5000 seu-usuario/youtube-downloader:latest
```

## 🧪 Testes

```bash
# Instalar dependências de teste
pip install pytest pytest-flask

# Executar testes
pytest
```

## 📝 Uso

1. Acesse a interface web
2. Cole a URL do vídeo do YouTube
3. Clique em "Validar"
4. Visualize o preview com informações do vídeo
5. Escolha a qualidade desejada
6. Clique em "Baixar Vídeo"
7. O download será iniciado automaticamente

## ⚠️ Avisos Legais

- Use este serviço de forma responsável
- Respeite os direitos autorais dos criadores de conteúdo
- Este projeto é apenas para fins educacionais
- Verifique os Termos de Serviço do YouTube antes de usar

## 🔧 Troubleshooting

### Erro: "yt-dlp não encontrado"

```bash
pip install --upgrade yt-dlp
```

### Erro: "CORS blocked"

Certifique-se de que o backend está rodando e configurado corretamente para aceitar requisições do frontend.

### Erro: "Vídeo não disponível"

Alguns vídeos podem ter restrições de região ou privacidade que impedem o download.

## 🤝 Contribuindo

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

## 👤 Autor

Desenvolvido com ❤️ usando Flask e yt-dlp

## 🙏 Agradecimentos

- [yt-dlp](https://github.com/yt-dlp/yt-dlp) - Ferramenta de download
- [Flask](https://flask.palletsprojects.com/) - Framework web
- Comunidade open source

---

⭐ Se este projeto foi útil, considere dar uma estrela!
