"""
Configuración de pytest y fixtures compartidos
"""
import pytest
import os
import sys
from datetime import datetime

# Agregar el directorio backend al path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from models import db, User, Account, Category, Transaction
from werkzeug.security import generate_password_hash


@pytest.fixture(scope='session')
def app():
    """Crear aplicación Flask para testing"""
    app = create_app('testing')
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture(scope='function')
def client(app):
    """Cliente de prueba para hacer requests"""
    return app.test_client()


@pytest.fixture(scope='function')
def db_session(app):
    """Sesión de base de datos limpia para cada test"""
    with app.app_context():
        # Limpiar todas las tablas
        db.session.remove()
        db.drop_all()
        db.create_all()
        
        yield db
        
        # Limpiar después del test
        db.session.remove()
        db.drop_all()


@pytest.fixture
def test_user(db_session):
    """Crear usuario de prueba"""
    user = User(
        username='testuser',
        email='test@example.com',
        password_hash=generate_password_hash('testpassword123')
    )
    db_session.session.add(user)
    db_session.session.commit()
    return user


@pytest.fixture
def test_user_token(client, test_user):
    """Obtener token JWT para usuario de prueba"""
    response = client.post('/api/auth/login', json={
        'identifier': 'test@example.com',
        'password': 'testpassword123'
    })
    data = response.get_json()
    return data['access_token']


@pytest.fixture
def auth_headers(test_user_token):
    """Headers de autenticación para requests"""
    return {
        'Authorization': f'Bearer {test_user_token}',
        'Content-Type': 'application/json'
    }


@pytest.fixture
def test_account(db_session, test_user):
    """Crear cuenta de prueba"""
    account = Account(
        user_id=test_user.id,
        name='Test Account',
        account_type='checking',
        currency='USD',
        initial_balance=1000.0,
        current_balance=1000.0
    )
    db_session.session.add(account)
    db_session.session.commit()
    return account


@pytest.fixture
def test_category(db_session, test_user):
    """Crear categoría de prueba"""
    category = Category(
        user_id=test_user.id,
        name='Test Category',
        category_type='expense',
        icon='fa-test',
        color='#FF0000'
    )
    db_session.session.add(category)
    db_session.session.commit()
    return category


@pytest.fixture
def test_transaction(db_session, test_user, test_account, test_category):
    """Crear transacción de prueba"""
    transaction = Transaction(
        user_id=test_user.id,
        account_id=test_account.id,
        category_id=test_category.id,
        transaction_type='expense',
        amount=50.0,
        description='Test transaction',
        transaction_date=datetime.utcnow()
    )
    db_session.session.add(transaction)
    db_session.session.commit()
    return transaction
