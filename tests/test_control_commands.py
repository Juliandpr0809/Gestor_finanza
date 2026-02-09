"""
Script de prueba para comandos de control de usuario
Prueba los nuevos comandos de chat: cambiar balance, eliminar transacciones, etc.
"""
import requests
import json

# Configuración
BASE_URL = "http://localhost:5000/api"
TOKEN = None  # Se obtendrá después del login

def print_section(title):
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def login():
    """Iniciar sesión y obtener token"""
    global TOKEN
    print_section("1. INICIAR SESIÓN")
    
    response = requests.post(f"{BASE_URL}/auth/login", json={
        "email": "test@example.com",
        "password": "password123"
    })
    
    if response.status_code == 200:
        data = response.json()
        TOKEN = data['token']
        print(f"✅ Login exitoso. Token: {TOKEN[:20]}...")
        return True
    else:
        print(f"❌ Error en login: {response.status_code}")
        print(response.json())
        return False

def send_chat_message(message):
    """Enviar mensaje al chat"""
    headers = {"Authorization": f"Bearer {TOKEN}"}
    
    response = requests.post(
        f"{BASE_URL}/chat/send",
        headers=headers,
        json={"content": message}
    )
    
    if response.status_code in [200, 201]:
        data = response.json()
        return data
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.json())
        return None

def init_chat():
    """Inicializar chat si es necesario"""
    print_section("2. INICIALIZAR CHAT")
    
    headers = {"Authorization": f"Bearer {TOKEN}"}
    response = requests.post(f"{BASE_URL}/chat/init", headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Chat inicializado: {data.get('message', 'OK')}")
        
        if not data.get('initialized'):
            # Configurar moneda
            print("\n🔹 Configurando moneda COP...")
            result = send_chat_message("COP")
            if result:
                print(f"✅ Moneda configurada")
                print(f"Respuesta: {result['assistant_message']['content'][:100]}...")
    else:
        print(f"❌ Error: {response.status_code}")

def get_accounts():
    """Obtener cuentas del usuario"""
    print_section("3. VERIFICAR CUENTAS")
    
    headers = {"Authorization": f"Bearer {TOKEN}"}
    response = requests.get(f"{BASE_URL}/accounts", headers=headers)
    
    if response.status_code == 200:
        accounts = response.json()
        print(f"✅ Tienes {len(accounts)} cuenta(s):")
        for acc in accounts:
            print(f"   - {acc['name']}: {acc['currency']} {acc['current_balance']:,.2f}")
        return accounts
    else:
        print(f"❌ Error: {response.status_code}")
        return []

def test_change_balance_command():
    """Probar comando de cambiar balance"""
    print_section("4. PROBAR: CAMBIAR BALANCE")
    
    # Enviar comando
    print("\n🔹 Enviando: 'Cambiar mi balance a 200000'")
    result = send_chat_message("Cambiar mi balance a 200000")
    
    if result:
        response = result['assistant_message']['content']
        print(f"\n📩 Respuesta del sistema:")
        print(response)
        
        # Verificar que pida confirmación
        if "CONFIRMACIÓN" in response and "CONFIRMAR" in response:
            print("\n✅ Sistema solicita confirmación correctamente")
            return True
        else:
            print("\n❌ El sistema no solicitó confirmación")
            return False
    else:
        print("\n❌ No hubo respuesta del sistema")
        return False

def test_confirmation():
    """Probar confirmación del cambio"""
    print_section("5. PROBAR: CONFIRMAR CAMBIO")
    
    # Enviar confirmación
    print("\n🔹 Enviando: 'CONFIRMAR'")
    result = send_chat_message("CONFIRMAR")
    
    if result:
        response = result['assistant_message']['content']
        print(f"\n📩 Respuesta del sistema:")
        print(response)
        
        # Verificar que confirmó el cambio
        if "actualizado correctamente" in response or "Balance nuevo" in response:
            print("\n✅ Balance actualizado correctamente")
            return True
        else:
            print("\n❌ El cambio no se aplicó")
            return False
    else:
        print("\n❌ No hubo respuesta del sistema")
        return False

def test_delete_transaction_command():
    """Probar comando de eliminar transacción"""
    print_section("6. PROBAR: COMANDO ELIMINAR TRANSACCIÓN")
    
    # Enviar comando
    print("\n🔹 Enviando: 'Borrar transacción'")
    result = send_chat_message("Borrar transacción")
    
    if result:
        response = result['assistant_message']['content']
        print(f"\n📩 Respuesta del sistema:")
        print(response)
        
        # Verificar que muestre lista de transacciones
        if "últimas transacciones" in response.lower() or "ID" in response:
            print("\n✅ Sistema muestra lista de transacciones")
            return True
        else:
            print("\n❌ El sistema no mostró transacciones")
            return False
    else:
        print("\n❌ No hubo respuesta del sistema")
        return False

def test_edit_transaction_command():
    """Probar comando de editar transacción"""
    print_section("7. PROBAR: COMANDO EDITAR TRANSACCIÓN")
    
    # Enviar comando
    print("\n🔹 Enviando: 'Editar transacción'")
    result = send_chat_message("Editar transacción")
    
    if result:
        response = result['assistant_message']['content']
        print(f"\n📩 Respuesta del sistema:")
        print(response)
        
        # Verificar que muestre lista de transacciones
        if "editar" in response.lower() and "ID" in response:
            print("\n✅ Sistema muestra opciones de edición")
            return True
        else:
            print("\n❌ El sistema no mostró opciones")
            return False
    else:
        print("\n❌ No hubo respuesta del sistema")
        return False

def test_reset_balance_command():
    """Probar comando de resetear balance"""
    print_section("8. PROBAR: COMANDO RESETEAR BALANCE")
    
    # Enviar comando
    print("\n🔹 Enviando: 'Resetear balance'")
    result = send_chat_message("Resetear balance")
    
    if result:
        response = result['assistant_message']['content']
        print(f"\n📩 Respuesta del sistema:")
        print(response)
        
        # Verificar que pida confirmación
        if "CONFIRMACIÓN" in response and "resetear" in response.lower():
            print("\n✅ Sistema solicita confirmación para reseteo")
            return True
        else:
            print("\n❌ El sistema no solicitó confirmación")
            return False
    else:
        print("\n❌ No hubo respuesta del sistema")
        return False

def test_regular_transaction():
    """Probar que las transacciones normales sigan funcionando"""
    print_section("9. PROBAR: TRANSACCIÓN NORMAL")
    
    # Enviar transacción regular
    print("\n🔹 Enviando: 'Gasté 50 en gasolina'")
    result = send_chat_message("Gasté 50 en gasolina")
    
    if result:
        response = result['assistant_message']['content']
        print(f"\n📩 Respuesta del sistema:")
        print(response[:300] + "...")
        
        # Verificar que creó la transacción
        if "Transacción registrada" in response or "registrada" in response.lower():
            print("\n✅ Transacción normal funciona correctamente")
            return True
        else:
            print("\n❌ La transacción no se creó")
            return False
    else:
        print("\n❌ No hubo respuesta del sistema")
        return False

def run_all_tests():
    """Ejecutar todos los tests"""
    print("\n" + "🎯"*30)
    print("  TEST SUITE: CONTROL DE USUARIO VIA CHAT")
    print("🎯"*30)
    
    results = []
    
    # 1. Login
    if not login():
        print("\n❌ FALLO CRÍTICO: No se pudo hacer login")
        return
    
    # 2. Inicializar chat
    init_chat()
    
    # 3. Verificar cuentas
    accounts = get_accounts()
    if not accounts:
        print("\n⚠️ ADVERTENCIA: No hay cuentas, algunos tests pueden fallar")
    
    # 4-9. Tests de comandos
    results.append(("Comando Cambiar Balance", test_change_balance_command()))
    results.append(("Confirmación de Cambio", test_confirmation()))
    results.append(("Comando Eliminar Transacción", test_delete_transaction_command()))
    results.append(("Comando Editar Transacción", test_edit_transaction_command()))
    results.append(("Comando Resetear Balance", test_reset_balance_command()))
    results.append(("Transacción Normal", test_regular_transaction()))
    
    # Resumen de resultados
    print_section("RESUMEN DE RESULTADOS")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print(f"\n{'='*60}")
    print(f"  Total: {passed}/{total} tests pasaron")
    
    if passed == total:
        print(f"  🎉 TODOS LOS TESTS PASARON! 🎉")
    elif passed > 0:
        print(f"  ⚠️ ALGUNOS TESTS FALLARON")
    else:
        print(f"  ❌ TODOS LOS TESTS FALLARON")
    
    print(f"{'='*60}\n")

if __name__ == "__main__":
    try:
        run_all_tests()
    except Exception as e:
        print(f"\n❌ ERROR FATAL: {e}")
        import traceback
        traceback.print_exc()
