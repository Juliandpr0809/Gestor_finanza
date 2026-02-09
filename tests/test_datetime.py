"""
Test rápido para verificar formato de fecha/hora
"""
from datetime import datetime

# Simular una transacción
transaction_date = datetime.utcnow()

# Formato actual (sin hora)
formato_viejo = transaction_date.strftime('%d/%m/%Y')
print(f"Formato viejo (sin hora): {formato_viejo}")

# Formato nuevo (con hora)
formato_nuevo = transaction_date.strftime('%d/%m/%Y %H:%M')
print(f"Formato nuevo (con hora): {formato_nuevo}")

# Formato con segundos
formato_completo = transaction_date.strftime('%d/%m/%Y %H:%M:%S')
print(f"Formato completo: {formato_completo}")

# ISO format (para JavaScript)
formato_iso = transaction_date.isoformat()
print(f"Formato ISO: {formato_iso}")
