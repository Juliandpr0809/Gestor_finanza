"""
Utilidades de validación y sanitización
"""
import bleach
import re
from marshmallow import ValidationError

def sanitize_html(text):
    """
    Sanitizar HTML peligroso de un texto
    Permite texto plano, remueve tags HTML
    """
    if not text:
        return text
    return bleach.clean(text, tags=[], strip=True)

def sanitize_input(data):
    """
    Sanitizar inputs de texto en un diccionario
    """
    if isinstance(data, dict):
        return {key: sanitize_input(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [sanitize_input(item) for item in data]
    elif isinstance(data, str):
        return sanitize_html(data)
    else:
        return data

def validate_and_sanitize(schema, data):
    """
    Validar datos con un schema y sanitizar inputs
    
    Args:
        schema: Instancia de Schema de Marshmallow
        data: Diccionario con datos a validar
        
    Returns:
        Datos validados y sanitizados
        
    Raises:
        ValidationError: Si la validación falla
    """
    # Primero sanitizar
    sanitized_data = sanitize_input(data)
    
    # Luego validar
    validated_data = schema.load(sanitized_data)
    
    return validated_data

def is_safe_redirect_url(url):
    """
    Verificar que una URL de redirect sea segura
    """
    if not url:
        return False
    
    # Solo permitir URLs relativas o del mismo dominio
    if url.startswith('/'):
        return True
    
    # Bloquear javascript: y data: URLs
    dangerous_schemes = ['javascript:', 'data:', 'vbscript:']
    if any(url.lower().startswith(scheme) for scheme in dangerous_schemes):
        return False
    
    return False

def validate_file_extension(filename, allowed_extensions):
    """
    Validar extensión de archivo
    
    Args:
        filename: Nombre del archivo
        allowed_extensions: Lista de extensiones permitidas (ej: ['jpg', 'png'])
    """
    if not filename or '.' not in filename:
        return False
    
    ext = filename.rsplit('.', 1)[1].lower()
    return ext in allowed_extensions

def sanitize_filename(filename):
    """
    Sanitizar nombre de archivo
    """
    if not filename:
        return None
    
    # Remover caracteres peligrosos
    filename = re.sub(r'[^\w\s.-]', '', filename)
    
    # Limitar longitud
    if len(filename) > 255:
        filename = filename[:255]
    
    return filename
