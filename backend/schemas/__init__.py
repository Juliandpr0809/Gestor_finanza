"""
Schemas de validación con Marshmallow
"""
from marshmallow import Schema, fields, validate, validates, ValidationError
from datetime import datetime
import re

class UserRegisterSchema(Schema):
    """Schema para registro de usuario"""
    username = fields.Str(
        required=True,
        validate=[
            validate.Length(min=3, max=80, error="Username debe tener entre 3 y 80 caracteres"),
            validate.Regexp(r'^[a-zA-Z0-9_]+$', error="Username solo puede contener letras, números y guiones bajos")
        ]
    )
    email = fields.Email(required=True, error="Email inválido")
    password = fields.Str(
        required=True,
        validate=validate.Length(min=6, max=128, error="Password debe tener entre 6 y 128 caracteres")
    )

class UserLoginSchema(Schema):
    """Schema para login de usuario"""
    identifier = fields.Str(required=True, validate=validate.Length(min=3, max=120))
    password = fields.Str(required=True, validate=validate.Length(min=1, max=128))

class AccountSchema(Schema):
    """Schema para cuentas"""
    name = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=100, error="Nombre debe tener entre 1 y 100 caracteres")
    )
    account_type = fields.Str(
        required=True,
        validate=validate.OneOf(
            ['checking', 'savings', 'cash', 'credit_card', 'investment'],
            error="Tipo de cuenta inválido"
        )
    )
    currency = fields.Str(
        required=False,
        validate=validate.OneOf(
            ['USD', 'EUR', 'GBP', 'COP', 'MXN', 'ARS', 'BRL'],
            error="Moneda no soportada"
        )
    )
    initial_balance = fields.Float(required=False, validate=validate.Range(min=-1000000000, max=1000000000))
    current_balance = fields.Float(required=False, validate=validate.Range(min=-1000000000, max=1000000000))
    is_active = fields.Bool(required=False)

class TransactionSchema(Schema):
    """Schema para transacciones"""
    account_id = fields.Int(required=True, validate=validate.Range(min=1))
    category_id = fields.Int(required=True, validate=validate.Range(min=1))
    transaction_type = fields.Str(
        required=True,
        validate=validate.OneOf(['income', 'expense'], error="Tipo debe ser income o expense")
    )
    amount = fields.Float(
        required=True,
        validate=validate.Range(min=0.01, max=1000000000, error="Monto debe ser mayor a 0")
    )
    description = fields.Str(
        required=False,
        validate=validate.Length(max=255, error="Descripción máximo 255 caracteres")
    )
    notes = fields.Str(
        required=False,
        validate=validate.Length(max=1000, error="Notas máximo 1000 caracteres")
    )
    transaction_date = fields.DateTime(required=False)

    @validates('transaction_date')
    def validate_transaction_date(self, value):
        """Validar que la fecha no sea futura más de 1 día"""
        if value:
            if value > datetime.utcnow() + datetime.timedelta(days=1):
                raise ValidationError("La fecha de transacción no puede ser más de 1 día en el futuro")

class CategorySchema(Schema):
    """Schema para categorías"""
    name = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=100, error="Nombre debe tener entre 1 y 100 caracteres")
    )
    category_type = fields.Str(
        required=True,
        validate=validate.OneOf(['income', 'expense'], error="Tipo debe ser income o expense")
    )
    icon = fields.Str(
        required=False,
        validate=validate.Length(max=100, error="Icono máximo 100 caracteres")
    )
    color = fields.Str(
        required=False,
        validate=validate.Regexp(r'^#[0-9A-Fa-f]{6}$', error="Color debe ser hex válido (#RRGGBB)")
    )
    parent_id = fields.Int(required=False, validate=validate.Range(min=1))

class ChatMessageSchema(Schema):
    """Schema para mensajes de chat"""
    content = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=5000, error="Mensaje debe tener entre 1 y 5000 caracteres")
    )
