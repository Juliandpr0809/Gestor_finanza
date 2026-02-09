"""Script para verificar cuentas en la base de datos"""
from app import create_app
from models import db, User, Account

app = create_app()

with app.app_context():
    # Obtener todos los usuarios
    users = User.query.all()
    print(f"Total usuarios: {len(users)}\n")
    
    for user in users:
        print(f"Usuario ID: {user.id}")
        print(f"Email: {user.email}")
        print(f"Username: {user.username}")
        
        # Obtener cuentas del usuario
        accounts = Account.query.filter_by(user_id=user.id).all()
        print(f"Total cuentas: {len(accounts)}")
        
        for acc in accounts:
            print(f"  - {acc.name} ({acc.account_type}): ${acc.current_balance:,.2f} {acc.currency}")
            print(f"    Active: {acc.is_active}, ID: {acc.id}")
        
        print("-" * 50)
