"""
Tests para validación de datos con schemas de Marshmallow
"""
import pytest
from marshmallow import ValidationError
from schemas import (
    UserRegisterSchema, 
    UserLoginSchema, 
    AccountSchema, 
    TransactionSchema, 
    CategorySchema
)


class TestUserRegisterSchema:
    """Tests para validación de registro de usuario"""
    
    def test_valid_data(self):
        """Test: Datos válidos"""
        schema = UserRegisterSchema()
        data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'securepass123'
        }
        result = schema.load(data)
        assert result['email'] == 'test@example.com'
    
    def test_invalid_email(self):
        """Test: Email inválido"""
        schema = UserRegisterSchema()
        data = {
            'username': 'testuser',
            'email': 'invalid-email',
            'password': 'securepass123'
        }
        with pytest.raises(ValidationError) as exc_info:
            schema.load(data)
        assert 'email' in exc_info.value.messages
    
    def test_short_password(self):
        """Test: Contraseña muy corta"""
        schema = UserRegisterSchema()
        data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': '123'  # Menos de 6 caracteres
        }
        with pytest.raises(ValidationError) as exc_info:
            schema.load(data)
        assert 'password' in exc_info.value.messages
    
    def test_invalid_username(self):
        """Test: Username con caracteres inválidos"""
        schema = UserRegisterSchema()
        data = {
            'username': 'test user!@#',  # Espacios y caracteres especiales
            'email': 'test@example.com',
            'password': 'securepass123'
        }
        with pytest.raises(ValidationError) as exc_info:
            schema.load(data)
        assert 'username' in exc_info.value.messages


class TestAccountSchema:
    """Tests para validación de cuentas"""
    
    def test_valid_account(self):
        """Test: Cuenta válida"""
        schema = AccountSchema()
        data = {
            'name': 'My Account',
            'account_type': 'checking',
            'currency': 'USD',
            'initial_balance': 1000.0
        }
        result = schema.load(data)
        assert result['name'] == 'My Account'
    
    def test_invalid_account_type(self):
        """Test: Tipo de cuenta inválido"""
        schema = AccountSchema()
        data = {
            'name': 'My Account',
            'account_type': 'invalid_type',
            'currency': 'USD'
        }
        with pytest.raises(ValidationError) as exc_info:
            schema.load(data)
        assert 'account_type' in exc_info.value.messages
    
    def test_invalid_currency(self):
        """Test: Moneda no soportada"""
        schema = AccountSchema()
        data = {
            'name': 'My Account',
            'account_type': 'checking',
            'currency': 'XYZ'  # No soportada
        }
        with pytest.raises(ValidationError) as exc_info:
            schema.load(data)
        assert 'currency' in exc_info.value.messages


class TestTransactionSchema:
    """Tests para validación de transacciones"""
    
    def test_valid_transaction(self):
        """Test: Transacción válida"""
        schema = TransactionSchema()
        data = {
            'account_id': 1,
            'category_id': 1,
            'transaction_type': 'expense',
            'amount': 50.0,
            'description': 'Test transaction'
        }
        result = schema.load(data)
        assert result['amount'] == 50.0
    
    def test_invalid_transaction_type(self):
        """Test: Tipo de transacción inválido"""
        schema = TransactionSchema()
        data = {
            'account_id': 1,
            'category_id': 1,
            'transaction_type': 'invalid',
            'amount': 50.0
        }
        with pytest.raises(ValidationError) as exc_info:
            schema.load(data)
        assert 'transaction_type' in exc_info.value.messages
    
    def test_negative_amount(self):
        """Test: Monto negativo o cero"""
        schema = TransactionSchema()
        data = {
            'account_id': 1,
            'category_id': 1,
            'transaction_type': 'expense',
            'amount': -50.0
        }
        with pytest.raises(ValidationError) as exc_info:
            schema.load(data)
        assert 'amount' in exc_info.value.messages
    
    def test_description_too_long(self):
        """Test: Descripción muy larga"""
        schema = TransactionSchema()
        data = {
            'account_id': 1,
            'category_id': 1,
            'transaction_type': 'expense',
            'amount': 50.0,
            'description': 'X' * 300  # Más de 255 caracteres
        }
        with pytest.raises(ValidationError) as exc_info:
            schema.load(data)
        assert 'description' in exc_info.value.messages


class TestCategorySchema:
    """Tests para validación de categorías"""
    
    def test_valid_category(self):
        """Test: Categoría válida"""
        schema = CategorySchema()
        data = {
            'name': 'Food',
            'category_type': 'expense',
            'icon': 'fa-utensils',
            'color': '#FF5733'
        }
        result = schema.load(data)
        assert result['name'] == 'Food'
    
    def test_invalid_color_format(self):
        """Test: Color hex inválido"""
        schema = CategorySchema()
        data = {
            'name': 'Food',
            'category_type': 'expense',
            'color': 'red'  # No es formato hex
        }
        with pytest.raises(ValidationError) as exc_info:
            schema.load(data)
        assert 'color' in exc_info.value.messages
    
    def test_invalid_category_type(self):
        """Test: Tipo de categoría inválido"""
        schema = CategorySchema()
        data = {
            'name': 'Food',
            'category_type': 'invalid'
        }
        with pytest.raises(ValidationError) as exc_info:
            schema.load(data)
        assert 'category_type' in exc_info.value.messages
