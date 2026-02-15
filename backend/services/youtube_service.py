import yt_dlp
import os
import logging
import time
from pathlib import Path
from config import Config
from utils.validators import (
    validate_youtube_url, 
    ValidationError,
    validate_duration,
    sanitize_filename
)

logger = logging.getLogger(__name__)

class YouTubeService:
    """Serviço para interação com YouTube via yt-dlp"""
    
    def __init__(self):
        self.config = Config()
        self.download_dir = Path(self.config.DOWNLOAD_FOLDER)
        # Cache simples para evitar re-extração de info (TTL: 5 minutos)
        self._info_cache = {}
        self._cache_ttl = 300  # 5 minutos
    
    def _get_cached_info(self, video_id):
        """Retorna info do cache se ainda válida"""
        if video_id in self._info_cache:
            cached = self._info_cache[video_id]
            if time.time() - cached['timestamp'] < self._cache_ttl:
                logger.info(f"Usando cache para vídeo: {video_id}")
                return cached['data']
            else:
                # Cache expirado, remove
                del self._info_cache[video_id]
        return None

        def _apply_auth_options(self, options):
            """Aplica opções de autenticação do YouTube quando configuradas."""
            cookie_file = self.config.YT_COOKIES_FILE
            if cookie_file:
                if Path(cookie_file).exists():
                    options['cookiefile'] = cookie_file
                else:
                    logger.warning(f"YT_COOKIES_FILE configurado, mas arquivo não encontrado: {cookie_file}")
            return options
    
    def extract_video_info(self, url):
        """
        Extrai informações do vídeo sem fazer download
        
        Args:
            url (str): URL do YouTube
            
        Returns:
            dict: Informações do vídeo
            
        Raises:
            ValidationError: Se houver erro na extração
        """
        try:
            # Valida URL e extrai video ID
            video_id = validate_youtube_url(url)
            
            # Verifica cache primeiro
            cached_info = self._get_cached_info(video_id)
            if cached_info:
                return cached_info
            
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': False,
                # Headers para evitar bloqueio
                'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'referer': 'https://www.youtube.com/',
                'extractor_args': {
                    'youtube': {
                        'player_client': ['android'],  # Apenas Android, mais rápido
                        'player_skip': ['webpage', 'configs', 'js'],  # Pula mais coisas
                        'skip': ['hls', 'dash', 'translated_subs'],  # Não precisa disso para preview
                    }
                },
                # Otimizações de performance
                'nocheckcertificate': True,
                'socket_timeout': 6,  # Reduzido ainda mais
                'http_chunk_size': 10485760,
                'retries': 1,  # Apenas 1 tentativa para ser mais rápido
                'fragment_retries': 1,
                # Não baixar thumbnail ou legendas na validação
                'skip_download': True,
                'no_playlist': True,
                'ignoreerrors': False,
                # Não extrair formatos detalhados, só básico
                'format': 'best',
                'youtube_include_dash_manifest': False,
                'youtube_include_hls_manifest': False,
                'lazy_playlist': True,
                'age_limit': None,  # Não verifica restrição de idade
            }
            
            ydl_opts = self._apply_auth_options(ydl_opts)

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                logger.info(f"Extraindo informações do vídeo: {video_id}")
                info = ydl.extract_info(url, download=False)
                
                # Valida duração
                duration = info.get('duration', 0)
                validate_duration(duration, self.config.MAX_VIDEO_DURATION)
                
                # Qualidades padrão (não extrai de formatos para economizar tempo)
                qualities = self._get_available_qualities(info)
                
                result = {
                    'video_id': video_id,
                    'title': info.get('title', 'Sem título'),
                    'thumbnail': info.get('thumbnail', ''),
                    'duration': duration,
                    'duration_string': self._format_duration(duration),
                    'uploader': info.get('uploader', info.get('channel', 'Desconhecido')),
                    # Removido view_count para economizar tempo
                    'qualities': qualities,
                    'url': url
                }
                
                # Armazena no cache
                self._info_cache[video_id] = {
                    'data': result,
                    'timestamp': time.time()
                }
                
                logger.info(f"Informações extraídas com sucesso: {result['title']}")
                return result
                
        except ValidationError as e:
            logger.error(f"Erro de validação: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Erro ao extrair informações: {str(e)}")
            error_message = str(e)

            if "Sign in to confirm you’re not a bot" in error_message or "Sign in to confirm you're not a bot" in error_message:
                raise ValidationError(
                    "YouTube exigiu verificação anti-bot. Configure YT_COOKIES_FILE com um arquivo cookies.txt válido."
                )

            raise ValidationError(f"Erro ao processar vídeo: {error_message}")
    
    def download_video(self, url, quality='best', download_type='video'):
        """
        Faz download do vídeo ou áudio na qualidade especificada
        
        Args:
            url (str): URL do YouTube
            quality (str): Qualidade desejada
            download_type (str): Tipo de download - 'video' ou 'audio'
            
        Returns:
            dict: Informações do arquivo baixado
            
        Raises:
            ValidationError: Se houver erro no download
        """
        try:
            video_id = validate_youtube_url(url)
            
            # Configurar formato baseado no tipo e qualidade
            # Opções comuns para evitar erro 403
            common_opts = {
                'outtmpl': str(self.download_dir / '%(id)s.%(ext)s'),
                'quiet': True,
                'no_warnings': True,
                # Headers para evitar bloqueio do YouTube
                'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'referer': 'https://www.youtube.com/',
                # Opções para contornar restrições
                'extractor_args': {
                    'youtube': {
                        'player_client': ['android', 'web'],
                        'player_skip': ['webpage', 'configs'],
                    }
                },
                # Otimizações de performance
                'nocheckcertificate': True,
                'socket_timeout': 15,
                'http_chunk_size': 10485760,  # 10MB chunks para downloads mais rápidos
                'retries': 3,
                'fragment_retries': 3,
                'concurrent_fragment_downloads': 3,  # Download paralelo de fragmentos
                'no_playlist': True,
            }
            
            if download_type == 'audio':
                format_string = 'bestaudio/best'
                ydl_opts = {
                    **common_opts,
                    'format': format_string,
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '192',
                    }],
                }
            else:
                format_string = self._get_format_string(quality)
                ydl_opts = {
                    **common_opts,
                    'format': format_string,
                }

            ydl_opts = self._apply_auth_options(ydl_opts)
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                logger.info(f"Iniciando download: {video_id} ({download_type}) em qualidade {quality}")
                info = ydl.extract_info(url, download=True)
                
                # Encontrar o arquivo baixado
                filename = ydl.prepare_filename(info)
                file_path = Path(filename)
                
                # Para áudio, o arquivo será convertido para .mp3
                if download_type == 'audio':
                    file_path = file_path.with_suffix('.mp3')
                
                if not file_path.exists():
                    raise ValidationError("Arquivo não foi criado após o download")
                
                file_size = file_path.stat().st_size
                
                result = {
                    'video_id': video_id,
                    'title': info.get('title', 'video'),
                    'file_path': str(file_path),
                    'file_name': file_path.name,
                    'file_size': file_size,
                    'file_size_mb': round(file_size / (1024 * 1024), 2),
                    'ext': file_path.suffix,
                    'quality': quality,
                    'download_type': download_type
                }
                
                logger.info(f"Download concluído: {result['file_name']} ({result['file_size_mb']}MB)")
                return result
                
        except ValidationError as e:
            logger.error(f"Erro de validação no download: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Erro ao fazer download: {str(e)}")
            raise ValidationError(f"Erro no download: {str(e)}")
    
    def _get_available_qualities(self, info):
        """
        Extrai qualidades disponíveis dos formatos (versão otimizada)
        
        Args:
            info (dict): Informações do vídeo
            
        Returns:
            list: Lista de qualidades disponíveis
        """
        # Retorna qualidades padrão sem processar todos os formatos
        # Isso economiza tempo na extração
        qualities = [
            {
                'value': 'best',
                'label': 'Melhor qualidade',
                'note': 'Máxima qualidade disponível'
            },
            {
                'value': '1080p',
                'label': '1080p',
                'note': 'Full HD'
            },
            {
                'value': '720p',
                'label': '720p',
                'note': 'HD'
            },
            {
                'value': '480p',
                'label': '480p',
                'note': 'SD'
            },
            {
                'value': '360p',
                'label': '360p',
                'note': 'Baixa'
            }
        ]
        
        return qualities
    
    def _get_format_string(self, quality):
        """
        Converte qualidade em string de formato do yt-dlp
        
        Args:
            quality (str): Qualidade desejada
            
        Returns:
            str: String de formato para yt-dlp
        """
        if quality == 'best':
            return 'best'
        
        # Extrair altura da qualidade (ex: '720p' -> '720')
        height = quality.replace('p', '')
        
        # Formato: vídeo + áudio, altura específica ou menor
        return f'bestvideo[height<={height}]+bestaudio/best[height<={height}]/best'
    
    def _format_duration(self, seconds):
        """
        Formata duração em segundos para string legível
        
        Args:
            seconds (int): Duração em segundos
            
        Returns:
            str: Duração formatada (ex: "10:30")
        """
        if not seconds:
            return "0:00"
        
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60
        
        if hours > 0:
            return f"{hours}:{minutes:02d}:{secs:02d}"
        return f"{minutes}:{secs:02d}"
    
    def cleanup_old_files(self, max_age_seconds=3600):
        """
        Remove arquivos antigos do diretório de downloads
        
        Args:
            max_age_seconds (int): Idade máxima dos arquivos em segundos
        """
        try:
            import time
            current_time = time.time()
            
            for file_path in self.download_dir.iterdir():
                if file_path.is_file() and file_path.name != '.gitkeep':
                    file_age = current_time - file_path.stat().st_mtime
                    if file_age > max_age_seconds:
                        file_path.unlink()
                        logger.info(f"Arquivo removido: {file_path.name}")
        except Exception as e:
            logger.error(f"Erro ao limpar arquivos antigos: {str(e)}")


# Instância singleton do serviço
youtube_service = YouTubeService()
