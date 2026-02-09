from app import create_app
from models import db, Transaction, User, Account

app = create_app()
app.app_context().push()

print("=== Verificando transacciones ===\n")

# Ver todos los usuarios y sus transacciones
users = User.query.all()
print(f"Total de usuarios: {len(users)}\n")

for user in users:
    txs = Transaction.query.filter_by(user_id=user.id).all()
    print(f"Usuario: {user.username} (ID: {user.id})")
    print(f"  Email: {user.email}")
    print(f"  Transacciones: {len(txs)}")
    print()

# Ver transacciones sin usuario asignado
orphan_txs = Transaction.query.filter_by(user_id=None).all()
print(f"\nTransacciones sin usuario: {len(orphan_txs)}")

# Ver todas las transacciones con su información
all_txs = Transaction.query.all()
print(f"\nTotal de transacciones en DB: {len(all_txs)}")
if all_txs:
    print("\nPrimeras 5 transacciones:")
    for tx in all_txs[:5]:
        print(f"  ID: {tx.id}, User ID: {tx.user_id}, Type: {tx.transaction_type}, Amount: {tx.amount}, Date: {tx.transaction_date}")

# Ver cuentas
accounts = Account.query.all()
print(f"\nTotal de cuentas: {len(accounts)}")
for acc in accounts[:3]:
    print(f"  {acc.name} - User ID: {acc.user_id}")
