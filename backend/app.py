"""
Aplicación Flask principal - FinanceFlow
"""
import os
import sys
from dotenv import load_dotenv

# Configurar encoding UTF-8 para Windows
if sys.platform == 'win32':
    os.environ['PYTHONIOENCODING'] = 'utf-8'

# Cargar variables de entorno desde .env
load_dotenv()

from flask import Flask, jsonify, session, redirect, request, send_from_directory
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from config import config
from models import db, User, Account, Category, Transaction, ChatMessage, DEFAULT_CATEGORIES
from werkzeug.security import generate_password_hash
import click
from flask_migrate import Migrate
from datetime import datetime, timedelta

def create_app(config_name=None):
    """Factory para crear la aplicación Flask"""
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Inicializar extensiones
    db.init_app(app)
    Migrate(app, db)
    
    # CORS - Configuración según ambiente
    if config_name == 'development' or app.debug:
        # En desarrollo: CORS completamente abierto
        CORS(app, resources={
            r"/*": {
                "origins": "*",
                "allow_headers": ["Content-Type", "Authorization"],
                "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
                "supports_credentials": False
            }
        })
    else:
        # En producción: CORS con orígenes específicos
        CORS(app, resources={
            r"/api/*": {
                "origins": app.config['CORS_ORIGINS'],
                "allow_headers": ["Content-Type", "Authorization"],
                "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
                "supports_credentials": True
            }
        })
    # Rate Limiting - Protección contra abuso
    limiter = Limiter(
        app=app,
        key_func=get_remote_address,
        storage_uri=app.config['RATELIMIT_STORAGE_URL'],
        default_limits=[app.config['RATELIMIT_DEFAULT']],
        enabled=app.config['RATELIMIT_ENABLED']
    )
    
    # Headers de seguridad
    @app.after_request
    def security_headers(response):
        """Agregar headers de seguridad a todas las respuestas"""
        # Prevenir clickjacking
        response.headers['X-Frame-Options'] = 'DENY'
        # Prevenir MIME sniffing
        response.headers['X-Content-Type-Options'] = 'nosniff'
        # XSS Protection (legacy pero compatible)
        response.headers['X-XSS-Protection'] = '1; mode=block'
        
        # CSP más permisivo para desarrollo
        if config_name == 'development' or app.debug:
            # En desarrollo: permitir estilos inline, CDNs, y fetch a cualquier origen HTTPS (necesario para tunnels)
            response.headers['Content-Security-Policy'] = (
                "default-src 'self' https: data:; "
                "connect-src 'self' https: http: wss: ws:; "
                "style-src 'self' 'unsafe-inline' https://cdnjs.cloudflare.com https://cdn.jsdelivr.net https://unpkg.com; "
                "font-src 'self' data: https://cdnjs.cloudflare.com https://cdn.jsdelivr.net https://unpkg.com fonts.googleapis.com fonts.gstatic.com; "
                "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdnjs.cloudflare.com https://cdn.jsdelivr.net https://unpkg.com; "
                "img-src 'self' data: https: blob:; "
                "worker-src 'self';"
            )
        else:
            # En producción: más permisivo para CDNs de iconos y avatares
            response.headers['Content-Security-Policy'] = (
                "default-src 'self' https:; "
                "connect-src 'self' https: http:; "
                "style-src 'self' 'unsafe-inline' https://cdnjs.cloudflare.com https://cdn.jsdelivr.net https://unpkg.com; "
                "font-src 'self' data: https://cdnjs.cloudflare.com https://cdn.jsdelivr.net https://unpkg.com fonts.googleapis.com fonts.gstatic.com; "
                "script-src 'self' 'unsafe-inline' https://cdnjs.cloudflare.com https://cdn.jsdelivr.net https://unpkg.com; "
                "img-src 'self' data: https: blob:; "
                "worker-src 'self';"
            )
        
        # Referrer policy
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        return response
    
    # Crear contexto de aplicación
    with app.app_context():
        # Registrar blueprints
        from routes.auth import auth_bp
        from routes.accounts import accounts_bp
        from routes.transactions import transactions_bp
        from routes.categories import categories_bp
        from routes.chat import chat_bp
        
        app.register_blueprint(auth_bp, url_prefix='/api/auth')
        app.register_blueprint(accounts_bp, url_prefix='/api/accounts')
        app.register_blueprint(transactions_bp, url_prefix='/api/transactions')
        app.register_blueprint(categories_bp, url_prefix='/api/categories')
        app.register_blueprint(chat_bp, url_prefix='/api/chat')
    
    # Rutas de prueba
    @app.route('/', methods=['GET'])
    def welcome():
        """Redirigir a login del frontend"""
        return redirect('/frontend/html/login.html')
    
    @app.route('/manifest.json', methods=['GET', 'HEAD'])
    def serve_manifest():
        """Servir manifest.json - Importante para PWA"""
        try:
            frontend_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'frontend')
            return send_from_directory(frontend_path, 'manifest.json', mimetype='application/json')
        except Exception as e:
            app.logger.error(f"Error serving manifest.json: {e}")
            return '', 404
    
    @app.route('/service-worker.js', methods=['GET', 'HEAD'])
    def serve_service_worker():
        """Servir service-worker.js - Importante para PWA"""
        try:
            frontend_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'frontend')
            return send_from_directory(frontend_path, 'service-worker.js', mimetype='application/javascript')
        except Exception as e:
            app.logger.error(f"Error serving service-worker.js: {e}")
            return '', 404
    
    @app.route('/html/<path:filename>')
    @app.route('/<path:filename>')
    def serve_static_files(filename=None):
        """Servir archivos estáticos del frontend"""
        # Validar que filename no sea None
        if not filename:
            return '', 404

        # Compatibilidad: mapear /html/* a frontend/html/*
        if request.path.startswith('/html/') and not filename.startswith('html/'):
            filename = f'html/{filename}'
        
        # Evitar servir rutas de API con esta función
        if filename.startswith(('api/', 'health', 'info')):
            return '', 404
        
        # Evitar servir manifest.json y service-worker.js desde aqui
        if filename in ('manifest.json', 'service-worker.js'):
            return '', 404
        
        frontend_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'frontend')
        
        # Para archivos en subcarpetas (html, css, js, etc)
        if 'html/' in filename or 'css/' in filename or 'js/' in filename or 'images/' in filename:
            try:
                return send_from_directory(frontend_path, filename)
            except Exception:
                return '', 404
        
        # Por defecto, intentar buscar en frontend
        try:
            return send_from_directory(frontend_path, filename)
        except Exception:
            # Si no existe, devolver 404
            return '', 404
    
    @app.cli.command('seed')
    def seed_data():
        """Insertar datos de prueba: usuario demo, cuentas, categorías y transacciones."""
        existing = User.query.filter_by(email='demo@demo.com').first()
        if existing:
            click.echo('Seed ya aplicado: usuario demo@demo.com existe.')
            return

        user = User(
            username='demo',
            email='demo@demo.com',
            password_hash=generate_password_hash('demo1234')
        )
        db.session.add(user)
        db.session.commit()

        # No crear categorías por defecto - el usuario las crea según necesite

        # Cuentas demo
        accounts = [
            Account(user_id=user.id, name='Main Checking', account_type='checking', currency='USD', initial_balance=5000, current_balance=5000),
            Account(user_id=user.id, name='Savings', account_type='savings', currency='USD', initial_balance=12000, current_balance=12000),
        ]
        db.session.add_all(accounts)
        db.session.commit()

        # No crear transacciones de prueba - el usuario las crea según necesite

        click.echo('Seed aplicado. Usuario: demo@demo.com / demo1234')
    
    @app.route('/api', methods=['GET'])
    def api_info():
        """Página de bienvenida de la API"""
        return jsonify({
            'message': '💰 FinanceFlow API',
            'version': '0.1.0',
            'status': 'running',
            'endpoints': {
                'health': '/api/health',
                'info': '/api/info',
                'auth': {
                    'register': 'POST /api/auth/register',
                    'login': 'POST /api/auth/login',
                    'me': 'GET /api/auth/me'
                },
                'accounts': 'GET /api/accounts',
                'transactions': 'GET /api/transactions',
                'categories': 'GET /api/categories',
                'chat': {
                    'send': 'POST /api/chat/send',
                    'messages': 'GET /api/chat/messages',
                    'analyze': 'GET /api/chat/analyze'
                }
            },
            'demo_credentials': {
                'email': 'demo@demo.com',
                'password': 'demo1234'
            }
        }), 200
    
    @app.route('/api/health', methods=['GET'])
    def health():
        """Endpoint de salud"""
        return jsonify({'status': 'ok', 'message': 'FinanceFlow API running'}), 200
    
    @app.route('/api/info', methods=['GET'])
    def info():
        """Información de la API"""
        return jsonify({
            'app': 'FinanceFlow',
            'version': '0.1.0',
            'environment': config_name,
            'database': app.config['SQLALCHEMY_DATABASE_URI']
        }), 200
    
    @app.route('/favicon.ico')
    def favicon():
        """Favicon placeholder"""
        return '', 204
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5000)
