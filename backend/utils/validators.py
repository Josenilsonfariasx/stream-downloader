import re
from urllib.parse import urlparse, parse_qs

class ValidationError(Exception):
    """Exceção customizada para erros de validação"""
    pass

def validate_youtube_url(url):
    """
    Valida se a URL é do YouTube e retorna o video ID
    
    Args:
        url (str): URL para validar
        
    Returns:
        str: Video ID extraído da URL
        
    Raises:
        ValidationError: Se a URL for inválida
    """
    if not url or not isinstance(url, str):
        raise ValidationError("URL não fornecida ou inválida")
    
    url = url.strip()
    
    # Padrões de URL do YouTube
    youtube_patterns = [
        r'(?:https?://)?(?:www\.)?youtube\.com/watch\?v=([a-zA-Z0-9_-]{11})',
        r'(?:https?://)?(?:www\.)?youtu\.be/([a-zA-Z0-9_-]{11})',
        r'(?:https?://)?(?:www\.)?youtube\.com/embed/([a-zA-Z0-9_-]{11})',
        r'(?:https?://)?(?:www\.)?youtube\.com/v/([a-zA-Z0-9_-]{11})',
    ]
    
    for pattern in youtube_patterns:
        match = re.match(pattern, url)
        if match:
            return match.group(1)
    
    # Tentar extrair de query parameters
    try:
        parsed_url = urlparse(url)
        if 'youtube.com' in parsed_url.netloc or 'youtu.be' in parsed_url.netloc:
            query_params = parse_qs(parsed_url.query)
            if 'v' in query_params:
                video_id = query_params['v'][0]
                if len(video_id) == 11:
                    return video_id
    except Exception:
        pass
    
    raise ValidationError("URL do YouTube inválida")


def validate_quality(quality, available_qualities):
    """
    Valida se a qualidade escolhida está disponível
    
    Args:
        quality (str): Qualidade escolhida
        available_qualities (list): Lista de qualidades disponíveis
        
    Returns:
        str: Qualidade validada
        
    Raises:
        ValidationError: Se a qualidade for inválida
    """
    if not quality:
        return 'best'  # default
    
    quality = quality.strip().lower()
    
    if quality not in [q.lower() for q in available_qualities]:
        raise ValidationError(f"Qualidade '{quality}' não disponível")
    
    return quality


def sanitize_filename(filename):
    """
    Remove caracteres perigosos de um nome de arquivo
    
    Args:
        filename (str): Nome do arquivo para sanitizar
        
    Returns:
        str: Nome do arquivo sanitizado
    """
    # Remove caracteres perigosos
    dangerous_chars = ['/', '\\', '..', '<', '>', ':', '"', '|', '?', '*']
    for char in dangerous_chars:
        filename = filename.replace(char, '')
    
    # Limita tamanho
    if len(filename) > 200:
        filename = filename[:200]
    
    return filename.strip()


def validate_file_size(file_size, max_size):
    """
    Valida se o tamanho do arquivo está dentro do limite
    
    Args:
        file_size (int): Tamanho do arquivo em bytes
        max_size (int): Tamanho máximo permitido em bytes
        
    Returns:
        bool: True se válido
        
    Raises:
        ValidationError: Se o arquivo for muito grande
    """
    if file_size > max_size:
        raise ValidationError(
            f"Arquivo muito grande: {file_size / (1024*1024):.2f}MB. "
            f"Máximo permitido: {max_size / (1024*1024):.2f}MB"
        )
    return True


def validate_duration(duration, max_duration):
    """
    Valida se a duração do vídeo está dentro do limite
    
    Args:
        duration (int): Duração em segundos
        max_duration (int): Duração máxima permitida em segundos
        
    Returns:
        bool: True se válido
        
    Raises:
        ValidationError: Se o vídeo for muito longo
    """
    if duration > max_duration:
        raise ValidationError(
            f"Vídeo muito longo: {duration // 60} minutos. "
            f"Máximo permitido: {max_duration // 60} minutos"
        )
    return True
