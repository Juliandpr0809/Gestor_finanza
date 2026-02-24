"""
Configuración de la aplicación Flask
"""
import os
from datetime import timedelta
import secrets

class Config:
    """Configuración base"""
    # Base de datos
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///financeflow.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Secret Key - generar uno seguro si no existe
    SECRET_KEY = os.environ.get('SECRET_KEY') or secrets.token_urlsafe(32)
    
    # JWT
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or SECRET_KEY
    JWT_ALGORITHM = 'HS256'
    JWT_ACCESS_TOKEN_EXPIRES_MIN = int(os.environ.get('JWT_ACCESS_TOKEN_EXPIRES_MIN', 60 * 24))  # 24h
    
    # Sesiones - Configuración segura
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    SESSION_COOKIE_SECURE = os.environ.get('SESSION_COOKIE_SECURE', 'false').lower() == 'true'
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # CORS - Leer desde variable de entorno
    CORS_ORIGINS = os.environ.get('ALLOWED_ORIGINS', 
        'http://localhost:3000,http://127.0.0.1:3000,http://localhost:5173,http://localhost:5000,http://127.0.0.1:5000').split(',')
    
    # Rate Limiting
    RATELIMIT_ENABLED = os.environ.get('RATELIMIT_ENABLED', 'true').lower() == 'true'
    RATELIMIT_STORAGE_URL = os.environ.get('RATELIMIT_STORAGE_URL', 'memory://')
    RATELIMIT_DEFAULT = "100 per minute"  # Límite global por defecto
    RATELIMIT_STRATEGY = 'fixed-window'

class DevelopmentConfig(Config):
    """Configuración de desarrollo"""
    DEBUG = True
    TESTING = False
    ENV = 'development'
    # En desarrollo, permitir más requests
    RATELIMIT_DEFAULT = "200 per minute"
    # CORS permisivo para desarrollo (tunnels, etc)
    CORS_ORIGINS = ["*"]

class TestingConfig(Config):
    """Configuración de pruebas"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    RATELIMIT_ENABLED = False  # Deshabilitar rate limiting en tests

class ProductionConfig(Config):
    """Configuración de producción"""
    DEBUG = False
    TESTING = False
    # En producción, forzar cookies seguras
    SESSION_COOKIE_SECURE = True
    # Rate limiting: aumentado para desarrollo en PythonAnywhere
    RATELIMIT_DEFAULT = "500 per minute"

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

