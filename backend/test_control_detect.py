#!/usr/bin/env python3
"""
Script para testear detección de comandos de control
"""
import sys
sys.path.insert(0, '/c/Users/USER/Desktop/Gestor_finansas (2)/Gestor_finansas/backend')

from services.ai_service import ai_service

test_cases = [
    "Aplica esa transacción",
    "Edita esa transacción",
    "Cambiar esa transacción",
    "Modifica la transacción",
    "Aplícalo",
    "Hazlo",
]

print("=" * 70)
print("TESTING CONTROL COMMAND DETECTION")
print("=" * 70)

for test_msg in test_cases:
    print(f"\n📝 Input: '{test_msg}'")
    
    # Limpieza
    cleaned = ai_service.clean_user_input(test_msg)
    print(f"   Cleaned: '{cleaned}'")
    
    # Control command detection
    control = ai_service.detect_control_command(cleaned)
    print(f"   Control: {control}")
    
    # Action intent (solo si no es control command)
    if not control:
        action = ai_service.detect_action_intent(cleaned)
        print(f"   Action:  {action}")

print("\n" + "=" * 70)
