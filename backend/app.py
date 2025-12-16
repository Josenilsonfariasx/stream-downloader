from flask import Flask, jsonify
from flask_cors import CORS
from config import Config
import logging
import os

def create_app(config_class=Config):
    """Factory para criar a aplicação Flask"""
    
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Configurar CORS
    CORS(app, resources={r"/api/*": {"origins": app.config['CORS_ORIGINS']}})
    
    # Configurar logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Registrar blueprints
    from routes.download import download_bp
    app.register_blueprint(download_bp, url_prefix='/api')
    
    # Error handlers
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            'error': 'Bad Request',
            'message': str(error)
        }), 400
    
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'error': 'Not Found',
            'message': 'Endpoint não encontrado'
        }), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({
            'error': 'Internal Server Error',
            'message': 'Erro interno do servidor'
        }), 500
    
    @app.route('/')
    def index():
        return jsonify({
            'status': 'online',
            'message': 'YouTube Downloader API',
            'version': '1.0.0'
        })
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=app.config['DEBUG']
    )
