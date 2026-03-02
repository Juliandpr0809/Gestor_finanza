#!/usr/bin/env python3
"""
Script para testear detección de acciones
"""
import sys
sys.path.insert(0, '/c/Users/USER/Desktop/Gestor_finansas (2)/Gestor_finansas/backend')

from services.ai_service import ai_service

test_cases = [
    "Aplica esa transacción",
    "Aplícalo",
    "Hazlo",
    "Cambia esa transacción",
    "Edita esa transacción",
    "OK",
    "Sí",
]

print("=" * 60)
print("TESTING ACTION DETECTION")
print("=" * 60)

for test_msg in test_cases:
    print(f"\n📝 Testing: '{test_msg}'")
    
    # Limpieza
    cleaned = ai_service.clean_user_input(test_msg)
    print(f"   Cleaned: '{cleaned}'")
    
    # Action intent
    action = ai_service.detect_action_intent(cleaned)
    print(f"   Action:  {action}")
    
    # Confirmation
    is_confirm = ai_service.detect_confirmation_words(cleaned)
    print(f"   Confirm: {is_confirm}")

print("\n" + "=" * 60)
