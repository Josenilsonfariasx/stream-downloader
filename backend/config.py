import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Diretórios base
BASE_DIR = Path(__file__).resolve().parent
DOWNLOAD_DIR = BASE_DIR.parent / 'downloads'

# Criar diretório de downloads se não existir
DOWNLOAD_DIR.mkdir(exist_ok=True)

class Config:
    """Configurações da aplicação"""
    
    # Flask
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.getenv('DEBUG', 'True') == 'True'
    
    # CORS
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', '*')
    
    # Diretórios
    DOWNLOAD_FOLDER = str(DOWNLOAD_DIR)
    
    # Limites de download
    MAX_VIDEO_DURATION = int(os.getenv('MAX_VIDEO_DURATION', 3600))  # segundos (1 hora)
    MAX_FILE_SIZE = int(os.getenv('MAX_FILE_SIZE', 500 * 1024 * 1024))  # bytes (500MB)
    
    # Tempo de limpeza de arquivos temporários
    TEMP_FILE_RETENTION = int(os.getenv('TEMP_FILE_RETENTION', 3600))  # segundos (1 hora)
    
    # yt-dlp options
    YT_DLP_OPTIONS = {
        'format': 'best',
        'outtmpl': os.path.join(DOWNLOAD_FOLDER, '%(id)s.%(ext)s'),
        'quiet': True,
        'no_warnings': True,
        'extract_flat': False,
    }

    # Autenticação opcional para YouTube (contornar bloqueio anti-bot)
    YT_COOKIES_FILE = os.getenv('YT_COOKIES_FILE', '').strip()
    YT_PROXY_URL = os.getenv('YT_PROXY_URL', '').strip()
    
    # Qualidades disponíveis
    AVAILABLE_QUALITIES = ['best', '1080p', '720p', '480p', '360p']
    
    # Rate limiting
    RATE_LIMIT_ENABLED = os.getenv('RATE_LIMIT_ENABLED', 'False') == 'True'
    RATE_LIMIT_PER_MINUTE = int(os.getenv('RATE_LIMIT_PER_MINUTE', 10))
