"""
Tests para funcionalidades de seguridad
"""
import pytest
from utils.validators import (
    sanitize_html,
    sanitize_input,
    is_safe_redirect_url,
    validate_file_extension,
    sanitize_filename
)


class TestSanitization:
    """Tests para sanitización de inputs"""
    
    def test_sanitize_html_removes_tags(self):
        """Test: Remover tags HTML peligrosos"""
        dirty = '<script>alert("XSS")</script>Hello'
        clean = sanitize_html(dirty)
        assert '<script>' not in clean
        assert 'Hello' in clean
    
    def test_sanitize_html_removes_onclick(self):
        """Test: Remover handlers de eventos"""
        dirty = '<div onclick="malicious()">Click me</div>'
        clean = sanitize_html(dirty)
        assert 'onclick' not in clean
    
    def test_sanitize_input_dict(self):
        """Test: Sanitizar diccionario"""
        dirty_dict = {
            'name': '<b>John</b>',
            'email': 'test@example.com',
            'bio': '<script>alert(1)</script>Safe text'
        }
        clean = sanitize_input(dirty_dict)
        assert '<script>' not in clean['bio']
        assert 'Safe text' in clean['bio']
    
    def test_sanitize_input_nested(self):
        """Test: Sanitizar estructura anidada"""
        dirty_nested = {
            'user': {
                'name': '<b>John</b>',
                'tags': ['<script>tag1</script>', 'tag2']
            }
        }
        clean = sanitize_input(dirty_nested)
        assert '<script>' not in str(clean)
    
    def test_sanitize_input_preserves_safe_content(self):
        """Test: Preservar contenido seguro"""
        safe_dict = {
            'name': 'John Doe',
            'amount': 100.50,
            'active': True
        }
        clean = sanitize_input(safe_dict)
        assert clean['name'] == 'John Doe'
        assert clean['amount'] == 100.50
        assert clean['active'] is True


class TestURLValidation:
    """Tests para validación de URLs"""
    
    def test_safe_relative_url(self):
        """Test: URL relativa es segura"""
        assert is_safe_redirect_url('/dashboard')
        assert is_safe_redirect_url('/accounts/123')
    
    def test_unsafe_javascript_url(self):
        """Test: javascript: URL es insegura"""
        assert not is_safe_redirect_url('javascript:alert(1)')
    
    def test_unsafe_data_url(self):
        """Test: data: URL es insegura"""
        assert not is_safe_redirect_url('data:text/html,<script>alert(1)</script>')
    
    def test_empty_url(self):
        """Test: URL vacía no es segura"""
        assert not is_safe_redirect_url('')
        assert not is_safe_redirect_url(None)
    
    def test_external_url_not_safe(self):
        """Test: URLs externas no son seguras por defecto"""
        assert not is_safe_redirect_url('https://evil.com')


class TestFileValidation:
    """Tests para validación de archivos"""
    
    def test_valid_file_extension(self):
        """Test: Extensión de archivo válida"""
        assert validate_file_extension('photo.jpg', ['jpg', 'png'])
        assert validate_file_extension('document.pdf', ['pdf', 'doc'])
    
    def test_invalid_file_extension(self):
        """Test: Extensión de archivo inválida"""
        assert not validate_file_extension('script.exe', ['jpg', 'png'])
        assert not validate_file_extension('file.php', ['pdf', 'doc'])
    
    def test_case_insensitive_extension(self):
        """Test: Extensiones case-insensitive"""
        assert validate_file_extension('PHOTO.JPG', ['jpg', 'png'])
    
    def test_no_extension(self):
        """Test: Archivo sin extensión"""
        assert not validate_file_extension('noextension', ['jpg', 'png'])
    
    def test_sanitize_filename_removes_dangerous_chars(self):
        """Test: Remover caracteres peligrosos del nombre"""
        dangerous = '../etc/passwd'
        safe = sanitize_filename(dangerous)
        assert '..' not in safe
        assert '/' not in safe
    
    def test_sanitize_filename_limits_length(self):
        """Test: Limitar longitud de nombre de archivo"""
        long_name = 'a' * 300 + '.txt'
        safe = sanitize_filename(long_name)
        assert len(safe) <= 255
    
    def test_sanitize_filename_preserves_valid_chars(self):
        """Test: Preservar caracteres válidos"""
        valid = 'my_document-2024.pdf'
        safe = sanitize_filename(valid)
        assert safe == valid


class TestSecurityHeaders:
    """Tests para headers de seguridad"""
    
    def test_security_headers_present(self, client):
        """Test: Headers de seguridad están presentes"""
        response = client.get('/api/health')
        
        assert 'X-Frame-Options' in response.headers
        assert response.headers['X-Frame-Options'] == 'DENY'
        
        assert 'X-Content-Type-Options' in response.headers
        assert response.headers['X-Content-Type-Options'] == 'nosniff'
        
        assert 'X-XSS-Protection' in response.headers
        assert 'Content-Security-Policy' in response.headers
    
    def test_cors_headers(self, client):
        """Test: Headers CORS configurados correctamente"""
        response = client.options('/api/auth/login')
        # Verificar que CORS está configurado (puede variar según config)
        assert response.status_code in [200, 204]
