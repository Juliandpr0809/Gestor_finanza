#!/usr/bin/env python3
"""
Script completo de pruebas ejecutando Flask en subprocess
"""
import subprocess
import time
import sys
import os
import json

# Cambiar al directorio backend
os.chdir('c:/Users/USER/Desktop/Gestor_finansas/backend')
sys.path.insert(0, 'c:/Users/USER/Desktop/Gestor_finansas/backend')

# Iniciar servidor Flask en background
print("🚀 Iniciando servidor Flask...")
proc = subprocess.Popen(
    ['python', 'app.py'],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    cwd='c:/Users/USER/Desktop/Gestor_finansas/backend'
)

# Esperar a que inicie
time.sleep(5)

# Ahora hacer pruebas
print("\n" + "="*60)
print("PRUEBAS DE ENDPOINTS")
print("="*60 + "\n")

import requests

BASE_URL = "http://localhost:5000/api"

# Test 1: Register
print("1️⃣  REGISTRO...")
import time as tm
unique_id = str(int(tm.time() * 1000))
resp = requests.post(f"{BASE_URL}/auth/register", json={
    "email": f"test_{unique_id}@example.com",
    "password": "TestPassword123!",
    "username": f"user_{unique_id}"
}).json()

if 'access_token' in resp:
    print("   ✅ Registro exitoso")
    token = resp['access_token']
else:
    print(f"   ❌ Error: {resp}")
    token = None

# Test 2: Get User Info
if token:
    print("\n2️⃣  OBTENER USUARIO...")
    resp = requests.get(
        f"{BASE_URL}/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    ).json()
    
    if 'preferred_currency' in resp:
        print(f"   ✅ Usuario obtenido: {resp['email']}, Moneda: {resp['preferred_currency']}")
    else:
        print(f"   ⚠️  Falta preferred_currency: {resp}")

# Test 3: Create Account
if token:
    print("\n3️⃣  CREAR CUENTA...")
    resp = requests.post(
        f"{BASE_URL}/accounts",
        json={
            "name": "Test Bank",
            "account_type": "checking",
            "currency": "USD",
            "initial_balance": 1000
        },
        headers={"Authorization": f"Bearer {token}"}
    ).json()
    
    if 'id' in resp:
        print(f"   ✅ Cuenta creada: {resp['name']}")
        account_id = resp['id']
    else:
        print(f"   ❌ Error: {resp}")
        account_id = None

# Test 4: Get Accounts
if token:
    print("\n4️⃣  LISTAR CUENTAS...")
    resp = requests.get(
        f"{BASE_URL}/accounts",
        headers={"Authorization": f"Bearer {token}"}
    ).json()
    
    if isinstance(resp, list) and len(resp) > 0:
        print(f"   ✅ {len(resp)} cuenta(s) encontrada(s)")
        for acc in resp:
            print(f"      • {acc['name']} ({acc['currency']}): {acc.get('current_balance', 'N/A')}")
    else:
        print(f"   ❌ Error: {resp}")

# Test 5: Create Category
if token:
    print("\n5️⃣  CREAR CATEGORÍA...")
    resp = requests.post(
        f"{BASE_URL}/categories",
        json={
            "name": "Food & Dining",
            "category_type": "expense",
            "icon": "fa-utensils",
            "color": "#FF6B6B"
        },
        headers={"Authorization": f"Bearer {token}"}
    ).json()
    
    if 'id' in resp:
        print(f"   ✅ Categoría creada: {resp['name']}")
        category_id = resp['id']
    else:
        print(f"   ❌ Error: {resp}")
        category_id = None

# Test 6: Create Transaction
if token and account_id and category_id:
    print("\n6️⃣  CREAR TRANSACCIÓN...")
    resp = requests.post(
        f"{BASE_URL}/transactions",
        json={
            "account_id": account_id,
            "category_id": category_id,
            "transaction_type": "expense",
            "amount": 50.00,
            "description": "Lunch at restaurant",
            "transaction_date": "2026-01-08"
        },
        headers={"Authorization": f"Bearer {token}"}
    ).json()
    
    if 'id' in resp:
        print(f"   ✅ Transacción creada: ${resp['amount']} - {resp['description']}")
        transaction_id = resp['id']
    else:
        print(f"   ❌ Error: {resp}")
        transaction_id = None

# Test 7: Init Chat
if token:
    print("\n7️⃣  INICIAR CHAT...")
    resp = requests.post(
        f"{BASE_URL}/chat/init",
        headers={"Authorization": f"Bearer {token}"}
    ).json()
    
    if 'message' in resp:
        print(f"   ✅ Chat inicializado")
        if resp.get('initialized') == False:
            print(f"   📝 Mensaje de bienvenida preparado (primeros 100 chars):")
            print(f"      {resp['message'][:100]}...")
    else:
        print(f"   ❌ Error: {resp}")

# Test 8: Set Currency
if token:
    print("\n8️⃣  ESTABLECER MONEDA...")
    resp = requests.post(
        f"{BASE_URL}/chat/set-currency",
        json={"currency": "COP"},
        headers={"Authorization": f"Bearer {token}"}
    ).json()
    
    if resp.get('success'):
        print(f"   ✅ Moneda establecida: {resp.get('currency')}")
    else:
        print(f"   ❌ Error: {resp}")

# Test 9: Send Chat Message
if token:
    print("\n9️⃣  ENVIAR MENSAJE AL CHAT...")
    resp = requests.post(
        f"{BASE_URL}/chat/send",
        json={"content": "Gasté 50.000 en supermercado hoy"},
        headers={"Authorization": f"Bearer {token}"}
    ).json()
    
    if 'assistant_message' in resp:
        print(f"   ✅ Mensaje enviado")
        print(f"   🤖 Respuesta: {resp['assistant_message']['content'][:150]}...")
    else:
        print(f"   ❌ Error: {resp}")

# Test 10: Get Chat History
if token:
    print("\n🔟 OBTENER HISTORIAL DE CHAT...")
    resp = requests.get(
        f"{BASE_URL}/chat/messages",
        headers={"Authorization": f"Bearer {token}"}
    ).json()
    
    if 'messages' in resp:
        print(f"   ✅ {len(resp['messages'])} mensaje(s) en historial")
        for msg in resp['messages'][:3]:  # Mostrar primeros 3
            role = "👤 Usuario" if msg['role'] == 'user' else "🤖 Asistente"
            print(f"      {role}: {msg['content'][:60]}...")
    else:
        print(f"   ❌ Error: {resp}")

print("\n" + "="*60)
print("✅ PRUEBAS COMPLETADAS")
print("="*60 + "\n")

# Terminar servidor
print("🛑 Deteniendo servidor...")
proc.terminate()
proc.wait(timeout=5)
print("✅ Servidor detenido\n")
