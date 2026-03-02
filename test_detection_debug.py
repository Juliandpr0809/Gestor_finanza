#!/usr/bin/env python3
"""Debug script para ver exactamente qué detecta el sistema"""
import sys
sys.path.insert(0, '/c/Users/USER/Desktop/Gestor_finansas (2)/Gestor_finansas/backend')
sys.path.insert(0, '/c/Users/USER/Desktop/Gestor_finansas (2)/Gestor_finansas')

from services.ai_service import ai_service

# Mensaje del usuario
message = "Gaste 70k en pasajes para semana en nu"

print(f"\n📝 Mensaje: {message}")
print(f"\n1. detect_local_first():")
result = ai_service.detect_local_first(message)
print(f"   Resultado: {result}")

print(f"\n2. detect_transaction_intent():")
result2 = ai_service.detect_transaction_intent(message)
print(f"   Resultado: {result2}")

print(f"\n3. clean_user_input():")
cleaned = ai_service.clean_user_input(message)
print(f"   Original: {message}")
print(f"   Limpio:   {cleaned}")

print(f"\n✅ Ambos deberían retornar intención válida con 'has_intent': True")
