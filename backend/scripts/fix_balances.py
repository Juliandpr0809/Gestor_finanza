"""
Script para recalcular los saldos de todas las cuentas
basándose en las transacciones existentes
"""
from app import create_app
from models import db, Account, Transaction

def recalculate_all_balances():
    """Recalcula los saldos de todas las cuentas"""
    app = create_app()
    
    with app.app_context():
        # Obtener todas las cuentas
        accounts = Account.query.all()
        
        print(f"Recalculando saldos para {len(accounts)} cuentas...\n")
        
        for account in accounts:
            # Resetear saldo al inicial
            account.current_balance = account.initial_balance
            
            # Obtener todas las transacciones de esta cuenta
            transactions = Transaction.query.filter_by(account_id=account.id).order_by(Transaction.transaction_date).all()
            
            print(f"Cuenta: {account.name} (ID: {account.id})")
            print(f"  Saldo inicial: ${account.initial_balance:.2f}")
            print(f"  Transacciones: {len(transactions)}")
            
            # Aplicar cada transacción normalizando monto positivo
            for trans in transactions:
                amount = abs(trans.amount)
                # Normalizar en BD para evitar montos negativos almacenados
                if trans.amount != amount:
                    trans.amount = amount
                if trans.transaction_type == 'income':
                    account.current_balance += amount
                    print(f"    + ${amount:.2f} (Ingreso: {trans.description})")
                else:  # expense
                    account.current_balance -= amount
                    print(f"    - ${amount:.2f} (Gasto: {trans.description})")
            
            print(f"  Saldo final: ${account.current_balance:.2f}\n")
        
        # Guardar todos los cambios
        db.session.commit()
        print("✅ Saldos recalculados correctamente!")

if __name__ == '__main__':
    recalculate_all_balances()
