import sys
import os

# Add parent directory to path to import app and models
# backend/utils -> backend
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db
from models import Account, Transaction

def reconcile_orphans():
    with app.app_context():
        print("=== INICIO DE RECONCILIACIÓN ===")
        
        # 1. Buscar transacciones huérfanas (sin cuenta asignada o cuenta inválida)
        orphans = Transaction.query.filter(
            (Transaction.account_id == None) | 
            (~Transaction.account_id.in_(db.session.query(Account.id)))
        ).all()
        
        if orphans:
            print(f"⚠️ Se encontraron {len(orphans)} transacciones huérfanas.")
            
            # Buscar cuenta "Efectivo" o primera disponible
            default_account = Account.query.filter(Account.name.ilike('%efectivo%')).first()
            if not default_account:
                default_account = Account.query.first()
            
            if default_account:
                print(f"🛠️ Asignando {len(orphans)} huérfanas a la cuenta: {default_account.name} (ID: {default_account.id})")
                for t in orphans:
                    t.account_id = default_account.id
                    # Ajustar balance
                    amount = abs(t.amount)
                    if t.transaction_type == 'expense':
                        default_account.current_balance -= amount
                    else:
                        default_account.current_balance += amount
                
                db.session.commit()
                print("✅ Transacciones huérfanas corregidas y asignadas.")
            else:
                print("❌ No hay cuentas disponibles. Crea una cuenta primero.")
        else:
            print("✅ No se encontraron transacciones huérfanas.")

        # 2. Recalcular balances para consistencia
        print("\n📊 Verificando consistencia de balances...")
        accounts = Account.query.all()
        
        for account in accounts:
            # Calcular balance real basado en transacciones
            # Balance = Inicial + Ingresos - Gastos
            
            incomes = db.session.query(db.func.sum(Transaction.amount)).filter(
                Transaction.account_id == account.id,
                Transaction.transaction_type == 'income'
            ).scalar() or 0
            
            expenses = db.session.query(db.func.sum(Transaction.amount)).filter(
                Transaction.account_id == account.id,
                Transaction.transaction_type == 'expense'
            ).scalar() or 0
            
            calculated_balance = account.initial_balance + incomes - expenses
            
            # Comparar con actual (permitir pequeña diferencia por float)
            diff = abs(account.current_balance - calculated_balance)
            
            if diff > 0.1:
                print(f"⚠️ Discrepancia en cuenta '{account.name}':")
                print(f"   - Balance guardado: {account.current_balance}")
                print(f"   - Balance calculado: {calculated_balance} (Ini: {account.initial_balance} + Inc: {incomes} - Exp: {expenses})")
                
                account.current_balance = calculated_balance
                account.updated_at = db.func.now()
                print(f"   ✅ Balance corregido a: {calculated_balance}")
            else:
                print(f"✅ Cuenta '{account.name}' consistente (Balance: {account.current_balance})")
        
        db.session.commit()
        print("\n=== RECONCILIACIÓN COMPLETADA ===")

if __name__ == '__main__':
    reconcile_orphans()
