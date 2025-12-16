from flask import Blueprint, request, jsonify, send_file
from services.youtube_service import youtube_service
from utils.validators import ValidationError
import logging
import os

logger = logging.getLogger(__name__)

download_bp = Blueprint('download', __name__)

@download_bp.route('/health', methods=['GET'])
def health_check():
    """Endpoint de health check"""
    return jsonify({
        'status': 'healthy',
        'service': 'youtube-downloader'
    }), 200


@download_bp.route('/validate', methods=['POST'])
def validate_video():
    """
    Valida URL do YouTube e retorna informações do vídeo
    
    Payload:
        {
            "url": "https://youtube.com/watch?v=..."
        }
    
    Response:
        {
            "success": true,
            "data": {
                "video_id": "...",
                "title": "...",
                "thumbnail": "...",
                "duration": 123,
                "duration_string": "2:03",
                "uploader": "...",
                "view_count": 12345,
                "qualities": [...]
            }
        }
    """
    try:
        data = request.get_json()
        
        if not data or 'url' not in data:
            return jsonify({
                'success': False,
                'error': 'URL não fornecida'
            }), 400
        
        url = data['url']
        
        # Limpar arquivos antigos antes de processar
        youtube_service.cleanup_old_files()
        
        # Extrair informações do vídeo
        video_info = youtube_service.extract_video_info(url)
        
        return jsonify({
            'success': True,
            'data': video_info
        }), 200
        
    except ValidationError as e:
        logger.warning(f"Erro de validação: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
        
    except Exception as e:
        logger.error(f"Erro no endpoint validate: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Erro ao processar vídeo'
        }), 500


@download_bp.route('/download', methods=['POST'])
def download_video():
    """
    Faz download do vídeo ou áudio e retorna o arquivo
    
    Payload:
        {
            "url": "https://youtube.com/watch?v=...",
            "quality": "720p",  // opcional, default: "best"
            "download_type": "video"  // opcional: "video" ou "audio", default: "video"
        }
    
    Response:
        Arquivo de vídeo ou áudio para download
    """
    try:
        data = request.get_json()
        
        if not data or 'url' not in data:
            return jsonify({
                'success': False,
                'error': 'URL não fornecida'
            }), 400
        
        url = data['url']
        quality = data.get('quality', 'best')
        download_type = data.get('download_type', 'video')
        
        logger.info(f"Requisição de download: {url} ({download_type}) em qualidade {quality}")
        
        # Fazer download do vídeo/áudio
        download_info = youtube_service.download_video(url, quality, download_type)
        
        file_path = download_info['file_path']
        
        # Verificar se o arquivo existe
        if not os.path.exists(file_path):
            return jsonify({
                'success': False,
                'error': 'Arquivo não encontrado após download'
            }), 500
        
        # Enviar arquivo
        mimetype = 'audio/mpeg' if download_info.get('download_type') == 'audio' else 'video/mp4'
        response = send_file(
            file_path,
            as_attachment=True,
            download_name=f"{download_info['title']}{download_info['ext']}",
            mimetype=mimetype
        )
        
        # Agendar limpeza do arquivo após envio
        @response.call_on_close
        def cleanup():
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
                    logger.info(f"Arquivo removido após envio: {file_path}")
            except Exception as e:
                logger.error(f"Erro ao remover arquivo: {str(e)}")
        
        return response
        
    except ValidationError as e:
        logger.warning(f"Erro de validação no download: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
        
    except Exception as e:
        logger.error(f"Erro no endpoint download: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Erro ao fazer download do vídeo'
        }), 500


@download_bp.route('/info', methods=['GET'])
def api_info():
    """Retorna informações sobre a API"""
    return jsonify({
        'endpoints': {
            '/api/health': 'Health check',
            '/api/validate': 'Validar URL e obter informações do vídeo',
            '/api/download': 'Fazer download do vídeo',
            '/api/info': 'Informações da API'
        },
        'version': '1.0.0',
        'documentation': 'https://github.com/seu-usuario/stream-downloader'
    }), 200
