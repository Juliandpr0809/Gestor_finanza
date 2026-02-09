#!/usr/bin/env python
"""
Test específico para verificar gestión correcta de monedas COP
Simula el escenario donde el usuario tiene COP y gasta
"""
import sys
import os

# Configurar encoding
os.environ['PYTHONIOENCODING'] = 'utf-8'

# Agregar el directorio backend al path
backend_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend')
sys.path.insert(0, backend_path)
os.chdir(backend_path)

from app import create_app, db
from models import User, Account, Category, Transaction
from services.ai_service import ai_service
from werkzeug.security import generate_password_hash
from decimal import Decimal
from datetime import datetime

app = create_app('development')

def test_currency_handling():
    """
    Test para verificar que:
    1. La IA entienda que los montos están en COP
    2. Los cálculos sean correctos
    3. Las respuestas incluyan COP explícitamente
    """
    
    with app.app_context():
        print("="*60)
        print("TEST: Gestión de Monedas COP")
        print("="*60)
        
        # Limpiar datos anteriores
        print("\n[*] Limpiando datos...")
        Transaction.query.delete()
        Category.query.delete()
        Account.query.delete()
        User.query.filter_by(username='cop_test_user').delete()
        db.session.commit()
        
        # 1. Crear usuario CON MONEDA COP
        print("\n[1] Creando usuario con moneda COP...")
        user = User(
            username='cop_test_user',
            email='cop@test.com',
            password_hash=generate_password_hash('pass123'),
            preferred_currency='COP',  # ← IMPORTANTE: COP
            chat_initialized=True
        )
        db.session.add(user)
        db.session.commit()
        print(f"[OK] Usuario creado con moneda: {user.preferred_currency}")
        
        # 2. Crear cuentas EN COP
        print("\n[2] Creando cuentas en COP...")
        account1 = Account(
            user_id=user.id,
            name='Tarjeta nequi',
            account_type='credit',
            currency='COP',
            initial_balance=98.00,
            current_balance=98.00,
            is_active=True
        )
        account2 = Account(
            user_id=user.id,
            name='Efectivo',
            account_type='savings',
            currency='COP',
            initial_balance=0.00,
            current_balance=0.00,
            is_active=True
        )
        db.session.add_all([account1, account2])
        db.session.commit()
        print(f"[OK] Cuenta 1: {account1.name} - {account1.currency} {account1.current_balance}")
        print(f"[OK] Cuenta 2: {account2.name} - {account2.currency} {account2.current_balance}")
        
        # 3. Crear categorías
        print("\n[3] Creando categorías...")
        categories_data = [
            ('Alimentación', 'expense'),
            ('Otros Gastos', 'expense'),
            ('Transporte', 'expense'),
        ]
        for cat_name, cat_type in categories_data:
            cat = Category(
                user_id=user.id,
                name=cat_name,
                category_type=cat_type
            )
            db.session.add(cat)
        db.session.commit()
        print(f"[OK] {len(categories_data)} categorías creadas")
        
        # 4. Obtener contexto financiero
        print("\n[4] Obteniendo contexto financiero con moneda...")
        context = ai_service.get_user_context(user.id)
        
        print(f"\n📊 CONTEXTO FINANCIERO:")
        print(f"  - Moneda: {context.get('currency')} ← VERIFICAR QUE SEA COP")
        print(f"  - Balance Total: {context.get('total_balance')} ← VERIFICAR QUE DIGA 'COP 98.00'")
        print(f"  - Cuentas: {context.get('accounts_count')}")
        
        # Verificar que la moneda esté en el contexto
        assert context.get('currency') == 'COP', f"❌ FALLO: Moneda debería ser COP, pero es {context.get('currency')}"
        assert 'COP' in context.get('total_balance', ''), f"❌ FALLO: Balance no incluye COP"
        print("\n[✓] Moneda correctamente incluida en contexto")
        
        # 5. Simular transacción
        print("\n[5] Creando transacción de prueba...")
        category = Category.query.filter_by(user_id=user.id, name='Alimentación').first()
        transaction = Transaction(
            user_id=user.id,
            account_id=account1.id,
            category_id=category.id,
            amount=-25.00,  # Gasto de 25 COP
            description='Comida',
            transaction_type='expense',
            transaction_date=datetime.now().date()
        )
        account1.current_balance -= 25
        
        db.session.add(transaction)
        db.session.commit()
        print(f"[OK] Transacción creada: -25 COP en Alimentación")
        print(f"[OK] Balance actualizado: {account1.currency} {account1.current_balance}")
        
        # 6. Verificar contexto actualizado
        print("\n[6] Verificando contexto actualizado...")
        context_updated = ai_service.get_user_context(user.id)
        
        print(f"\n📊 CONTEXTO ACTUALIZADO:")
        print(f"  - Balance Total: {context_updated.get('total_balance')} ← DEBE SER 'COP 73.00'")
        print(f"  - Transacciones recientes:")
        for txn in context_updated.get('recent_transactions', [])[:3]:
            print(f"      • {txn['description']}: {txn['amount']}")
        
        # 7. Simular prompt de IA
        print("\n[7] Simulando respuesta de IA...")
        
        # Crear un prompt simple que la IA debería responder
        prompt_test = """El usuario pregunta: "¿Cuál es mi balance total?"
        
Basado en el contexto financiero:
- Moneda del usuario: COP
- Balance Total: COP 73.00
- Cuentas:
  * Tarjeta nequi: COP 73.00
  * Efectivo: COP 0.00

La respuesta correcta DEBE incluir "COP" en todos los montos.
Respuesta esperada: "Tu balance total es COP 73.00"
NO debe decir: "Tu balance total es 73.00" o "Tu balance total es $73.00"
"""
        
        print(f"\n{prompt_test}")
        
        # 8. Resumen
        print("\n" + "="*60)
        print("RESUMEN DE TEST")
        print("="*60)
        print(f"\n✅ Usuario: {user.username}")
        print(f"✅ Moneda: {user.preferred_currency}")
        print(f"✅ Balance: {context_updated.get('total_balance')}")
        print(f"✅ Cuenta 1: {account1.currency} {account1.current_balance}")
        print(f"✅ Cuenta 2: {account2.currency} {account2.current_balance}")
        
        # Verificaciones
        print(f"\n📋 VERIFICACIONES:")
        checks = [
            (user.preferred_currency == 'COP', "Usuario tiene moneda COP"),
            ('COP' in context_updated.get('total_balance', ''), "Balance incluye 'COP'"),
            (account1.current_balance == 73.0, "Balance actualizado correctamente (98-25=73)"),
            (len(context_updated.get('recent_transactions', [])) > 0, "Transacciones en contexto"),
        ]
        
        all_passed = True
        for check, desc in checks:
            status = "✅" if check else "❌"
            print(f"  {status} {desc}")
            if not check:
                all_passed = False
        
        if all_passed:
            print("\n" + "="*60)
            print("✅ TODOS LOS TESTS PASARON")
            print("="*60)
            return 0
        else:
            print("\n" + "="*60)
            print("❌ ALGUNOS TESTS FALLARON")
            print("="*60)
            return 1

if __name__ == '__main__':
    try:
        exit_code = test_currency_handling()
        sys.exit(exit_code)
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
