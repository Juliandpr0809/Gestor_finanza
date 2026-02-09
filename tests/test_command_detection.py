"""
Test script para verificar la detección de comandos
"""
import sys
sys.path.insert(0, 'backend')

from services.ai_service import ai_service

# Test messages
test_messages = [
    "dejar cuentas en 0",
    "poner cuentas en 0",
    "elimina todas mis transacciones",
    "eliminar todas las transacciones",
    "elimina todas",
    "resetear balance",
]

print("=" * 60)
print("TESTING COMMAND DETECTION")
print("=" * 60)

for msg in test_messages:
    print(f"\n📝 Testing: '{msg}'")
    result = ai_service.detect_control_command(msg)
    
    if result and result.get('type') == 'control_command':
        print(f"✅ DETECTED: {result.get('action')}")
        print(f"   Full result: {result}")
    else:
        print(f"❌ NOT DETECTED")
        print(f"   Result: {result}")

print("\n" + "=" * 60)
