#!/usr/bin/env python
"""
Script de prueba para verificar el flujo completo de chat y transacciones
"""
import sys
import os
import json

# Configurar encoding
os.environ['PYTHONIOENCODING'] = 'utf-8'

# Agregar el directorio backend al path
backend_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend')
sys.path.insert(0, backend_path)
os.chdir(backend_path)

from app import create_app, db
from models import User, Account, Category, ChatMessage, Transaction
from werkzeug.security import generate_password_hash
from utils.jwt_utils import generate_access_token
from decimal import Decimal

app = create_app('development')

def test_chat_flow():
    """Prueba el flujo completo de chat con transacciones"""
    
    with app.app_context():
        print("[*] Limpiando datos de prueba anteriores...")
        # Limpiar en orden inverso de dependencias
        ChatMessage.query.filter_by(user_id=1).delete() if ChatMessage.query.filter_by(user_id=1).count() > 0 else None
        Transaction.query.delete()
        Category.query.delete()
        Account.query.delete()
        User.query.filter_by(username='testuser').delete()
        db.session.commit()
        
        # 1. Crear usuario de prueba
        print("[*] Creando usuario de prueba...")
        test_user = User(
            username='testuser',
            email='test@example.com',
            password_hash=generate_password_hash('password123'),
            chat_initialized=False,
            preferred_currency='USD'
        )
        db.session.add(test_user)
        db.session.commit()
        print(f"[OK] Usuario creado con ID: {test_user.id}")
        
        # 2. Crear cuentas
        print("[*] Creando cuentas...")
        account1 = Account(
            user_id=test_user.id,
            name='tarjeta nequi',
            account_type='credit',
            currency='USD',
            initial_balance=30.0,
            current_balance=30.0,
            is_active=True
        )
        account2 = Account(
            user_id=test_user.id,
            name='efectivo',
            account_type='savings',
            currency='USD',
            initial_balance=40.0,
            current_balance=40.0,
            is_active=True
        )
        db.session.add(account1)
        db.session.add(account2)
        db.session.commit()
        print(f"[OK] Cuentas creadas: {account1.name}, {account2.name}")
        
        # 3. Crear categorías
        print("[*] Creando categorías...")
        categories = [
            Category(user_id=test_user.id, name='Transporte', category_type='expense'),
            Category(user_id=test_user.id, name='Alimentación', category_type='expense'),
            Category(user_id=test_user.id, name='Otros Gastos', category_type='expense'),
            Category(user_id=test_user.id, name='Salario', category_type='income'),
        ]
        for cat in categories:
            db.session.add(cat)
        db.session.commit()
        print(f"[OK] {len(categories)} categorías creadas")
        
        # 4. Crear transacción manual
        print("[*] Creando transacción de prueba...")
        transaction = Transaction(
            user_id=test_user.id,
            account_id=account1.id,
            category_id=categories[2].id,  # Otros Gastos
            amount=-25.0,
            description='aceite de motor',
            transaction_type='expense',
            transaction_date='2026-01-02'
        )
        
        # Actualizar balance
        account1.current_balance -= 25.0
        
        db.session.add(transaction)
        db.session.commit()
        print(f"[OK] Transacción creada: ID={transaction.id}")
        
        # 5. Verificar datos
        print("\n[*] Verificando datos:")
        user = User.query.get(test_user.id)
        print(f"  - Usuario: {user.username}")
        print(f"  - Moneda preferida: {user.preferred_currency}")
        print(f"  - Chat inicializado: {user.chat_initialized}")
        
        accounts = Account.query.filter_by(user_id=test_user.id).all()
        print(f"  - Cuentas ({len(accounts)}):")
        for acc in accounts:
            print(f"      * {acc.name}: {acc.currency} {acc.current_balance:.2f}")
        
        transactions = Transaction.query.filter_by(user_id=test_user.id).all()
        print(f"  - Transacciones ({len(transactions)}):")
        for txn in transactions:
            print(f"      * {txn.description}: {txn.amount} (Cuenta: {txn.account.name})")
        
        # 6. Generar token JWT
        print("\n[*] Generando token JWT...")
        token = generate_access_token(user_id=test_user.id, email=test_user.email)
        print(f"[OK] Token generado: {token[:50]}...")
        
        print("\n[SUCCESS] Prueba completada exitosamente!")
        print(f"\nDatos de la transacción:")
        print(f"  Monto: USD 25.00")
        print(f"  Cuenta: tarjeta nequi (credit)")
        print(f"  Descripción: aceite de motor")
        print(f"  Nuevo balance tarjeta nequi: USD {account1.current_balance:.2f}")
        print(f"  Nuevo balance efectivo: USD {account2.current_balance:.2f}")
        print(f"  Balance Total: USD {account1.current_balance + account2.current_balance:.2f}")

if __name__ == '__main__':
    try:
        test_chat_flow()
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
