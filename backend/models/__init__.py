"""
Inicializador de la base de datos y SQLAlchemy
"""
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    """Modelo de Usuario"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    preferred_currency = db.Column(db.String(3), default='USD')  # Moneda preferida del usuario
    chat_initialized = db.Column(db.Boolean, default=False)  # Si ya se preguntó la moneda
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones
    accounts = db.relationship('Account', backref='user', lazy=True, cascade='all, delete-orphan')
    categories = db.relationship('Category', backref='user', lazy=True, cascade='all, delete-orphan')
    transactions = db.relationship('Transaction', backref='user', lazy=True, cascade='all, delete-orphan')
    chat_messages = db.relationship('ChatMessage', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<User {self.username}>'

class Account(db.Model):
    """Modelo de Cuenta"""
    __tablename__ = 'accounts'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    account_type = db.Column(db.String(50), nullable=False)  # banco, efectivo, tarjeta
    currency = db.Column(db.String(3), default='USD')
    initial_balance = db.Column(db.Float, default=0.0)
    current_balance = db.Column(db.Float, default=0.0)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones
    transactions = db.relationship('Transaction', backref='account', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Account {self.name}>'

class Category(db.Model):
    """Modelo de Categoría"""
    __tablename__ = 'categories'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    category_type = db.Column(db.String(50), nullable=False)  # income, expense
    icon = db.Column(db.String(100))  # emoji o clase CSS
    color = db.Column(db.String(7))  # código hex
    parent_id = db.Column(db.Integer, db.ForeignKey('categories.id'))  # Para subcategorías
    is_default = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relaciones
    subcategories = db.relationship(
        'Category',
        backref='parent',
        remote_side=[id],
        cascade='all, delete-orphan',
        single_parent=True
    )
    transactions = db.relationship('Transaction', backref='category', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Category {self.name}>'

class Transaction(db.Model):
    """Modelo de Transacción"""
    __tablename__ = 'transactions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    account_id = db.Column(db.Integer, db.ForeignKey('accounts.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    transaction_type = db.Column(db.String(50), nullable=False)  # income, expense
    amount = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(255))
    notes = db.Column(db.Text)
    transaction_date = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Transaction {self.description}>'

class ChatMessage(db.Model):
    """Modelo de Mensajes de Chat"""
    __tablename__ = 'chat_messages'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    role = db.Column(db.String(50), nullable=False)  # user, assistant
    content = db.Column(db.Text, nullable=False)
    message_metadata = db.Column(db.JSON)  # Información adicional (renombrado de metadata)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<ChatMessage {self.id}>'

class AccountBalanceBackup(db.Model):
    """Modelo para guardar snapshots de balances antes de cambios importantes"""
    __tablename__ = 'account_balance_backups'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    backup_type = db.Column(db.String(50), nullable=False)  # 'reset', 'manual_edit', etc
    backup_data = db.Column(db.JSON, nullable=False)  # {account_id: balance, ...}
    reason = db.Column(db.String(255))  # Razón del backup
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    restored_at = db.Column(db.DateTime)  # Cuándo se restauró (si aplica)
    
    def __repr__(self):
        return f'<AccountBalanceBackup user={self.user_id} type={self.backup_type}>'

# Categorías predefinidas
DEFAULT_CATEGORIES = {
    'income': [
        {'name': 'Salario', 'icon': 'fa-briefcase', 'color': '#FFFFFF'},
        {'name': 'Freelance', 'icon': 'fa-laptop-code', 'color': '#FFFFFF'},
        {'name': 'Inversiones', 'icon': 'fa-chart-line', 'color': '#FFFFFF'},
        {'name': 'Otros Ingresos', 'icon': 'fa-money-bill-wave', 'color': '#FFFFFF'},
    ],
    'expense': [
        {'name': 'Comida', 'icon': 'fa-utensils', 'color': '#FFFFFF'},
        {'name': 'Transporte', 'icon': 'fa-car', 'color': '#FFFFFF'},
        {'name': 'Vivienda', 'icon': 'fa-house', 'color': '#FFFFFF'},
        {'name': 'Servicios', 'icon': 'fa-bolt', 'color': '#FFFFFF'},
        {'name': 'Salud', 'icon': 'fa-heart-pulse', 'color': '#FFFFFF'},
        {'name': 'Entretenimiento', 'icon': 'fa-film', 'color': '#FFFFFF'},
        {'name': 'Educación', 'icon': 'fa-graduation-cap', 'color': '#FFFFFF'},
        {'name': 'Ropa', 'icon': 'fa-shirt', 'color': '#FFFFFF'},
        {'name': 'Otros', 'icon': 'fa-circle-question', 'color': '#FFFFFF'},
    ]
}
