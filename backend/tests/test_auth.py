"""
Tests para endpoints de autenticación
"""
import pytest
from models import User


class TestRegister:
    """Tests para el endpoint de registro"""
    
    def test_register_success(self, client, db_session):
        """Test: Registro exitoso de nuevo usuario"""
        response = client.post('/api/auth/register', json={
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'securepass123'
        })
        
        assert response.status_code == 201
        data = response.get_json()
        assert 'access_token' in data
        assert data['user']['email'] == 'newuser@example.com'
        
        # Verificar que el usuario existe en la BD
        user = User.query.filter_by(email='newuser@example.com').first()
        assert user is not None
    
    def test_register_duplicate_email(self, client, test_user):
        """Test: Error al registrar email duplicado"""
        response = client.post('/api/auth/register', json={
            'username': 'another',
            'email': 'test@example.com',  # Email ya existe
            'password': 'password123'
        })
        
        assert response.status_code == 409
        data = response.get_json()
        assert 'error' in data
    
    def test_register_invalid_email(self, client):
        """Test: Error con email inválido"""
        response = client.post('/api/auth/register', json={
            'username': 'user',
            'email': 'invalid-email',
            'password': 'password123'
        })
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
    
    def test_register_short_password(self, client):
        """Test: Error con contraseña muy corta"""
        response = client.post('/api/auth/register', json={
            'username': 'user',
            'email': 'valid@example.com',
            'password': '12345'  # Menos de 6 caracteres
        })
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
    
    def test_register_missing_fields(self, client):
        """Test: Error cuando faltan campos requeridos"""
        response = client.post('/api/auth/register', json={
            'email': 'test@example.com'
            # Falta password
        })
        
        assert response.status_code == 400


class TestLogin:
    """Tests para el endpoint de login"""
    
    def test_login_success_with_email(self, client, test_user):
        """Test: Login exitoso con email"""
        response = client.post('/api/auth/login', json={
            'identifier': 'test@example.com',
            'password': 'testpassword123'
        })
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'access_token' in data
        assert data['user']['email'] == 'test@example.com'
    
    def test_login_success_with_username(self, client, test_user):
        """Test: Login exitoso con username"""
        response = client.post('/api/auth/login', json={
            'identifier': 'testuser',
            'password': 'testpassword123'
        })
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'access_token' in data
    
    def test_login_wrong_password(self, client, test_user):
        """Test: Error con contraseña incorrecta"""
        response = client.post('/api/auth/login', json={
            'identifier': 'test@example.com',
            'password': 'wrongpassword'
        })
        
        assert response.status_code == 401
        data = response.get_json()
        assert 'error' in data
    
    def test_login_nonexistent_user(self, client):
        """Test: Error con usuario que no existe"""
        response = client.post('/api/auth/login', json={
            'identifier': 'nonexistent@example.com',
            'password': 'password123'
        })
        
        assert response.status_code == 401
    
    def test_login_missing_credentials(self, client):
        """Test: Error cuando faltan credenciales"""
        response = client.post('/api/auth/login', json={
            'identifier': 'test@example.com'
            # Falta password
        })
        
        assert response.status_code == 400


class TestGetCurrentUser:
    """Tests para el endpoint /me"""
    
    def test_get_current_user_success(self, client, test_user, auth_headers):
        """Test: Obtener usuario actual con token válido"""
        response = client.get('/api/auth/me', headers=auth_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['email'] == 'test@example.com'
        assert data['username'] == 'testuser'
    
    def test_get_current_user_no_token(self, client):
        """Test: Error sin token de autenticación"""
        response = client.get('/api/auth/me')
        
        assert response.status_code == 401
    
    def test_get_current_user_invalid_token(self, client):
        """Test: Error con token inválido"""
        headers = {
            'Authorization': 'Bearer invalid_token_here',
            'Content-Type': 'application/json'
        }
        response = client.get('/api/auth/me', headers=headers)
        
        assert response.status_code == 401


class TestLogout:
    """Tests para el endpoint de logout"""
    
    def test_logout_success(self, client, auth_headers):
        """Test: Logout exitoso"""
        response = client.post('/api/auth/logout', headers=auth_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'message' in data
