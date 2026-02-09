#!/usr/bin/env python3
"""
Script de prueba exhaustiva de todos los endpoints del sistema
"""

import requests
import json
import sys
from datetime import datetime

BASE_URL = "http://localhost:5000/api"

# Colores para output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def test(name, condition, details=""):
    """Helper para imprimir resultados de pruebas"""
    status = f"{GREEN}✅ PASS{RESET}" if condition else f"{RED}❌ FAIL{RESET}"
    print(f"  {status} {name}")
    if details and not condition:
        print(f"     {YELLOW}→ {details}{RESET}")

def section(title):
    """Imprimir sección de pruebas"""
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}{title}{RESET}")
    print(f"{BLUE}{'='*60}{RESET}")

# ==========================================
# TEST 1: AUTENTICACIÓN
# ==========================================
section("1. AUTENTICACIÓN - REGISTER & LOGIN")

token = None
user_email = f"test_{datetime.now().timestamp()}@test.com"
user_password = "TestPassword123!@#"

# Test Register
try:
    resp = requests.post(f"{BASE_URL}/auth/register", json={
        "email": user_email,
        "password": user_password,
        "username": f"testuser_{int(datetime.now().timestamp())}"
    })
    test("Register", resp.status_code in [200, 201], f"Status: {resp.status_code}")
    if resp.status_code in [200, 201]:
        data = resp.json()
        token = data.get('access_token')
        test("Token recibido", bool(token), "No se devolvió token")
except Exception as e:
    test("Register", False, str(e))

# Test Login
try:
    resp = requests.post(f"{BASE_URL}/auth/login", json={
        "identifier": user_email,
        "password": user_password
    })
    test("Login", resp.status_code == 200, f"Status: {resp.status_code}")
    if resp.status_code == 200:
        data = resp.json()
        token = data.get('access_token')
        test("Login token recibido", bool(token))
except Exception as e:
    test("Login", False, str(e))

# Test Get Current User
if token:
    try:
        resp = requests.get(
            f"{BASE_URL}/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        test("Get Current User", resp.status_code == 200, f"Status: {resp.status_code}")
        if resp.status_code == 200:
            user_data = resp.json()
            test("User email coincide", user_data.get('email') == user_email)
            test("Preferred currency existe", 'preferred_currency' in user_data)
    except Exception as e:
        test("Get Current User", False, str(e))

# ==========================================
# TEST 2: ACCOUNTS
# ==========================================
section("2. CUENTAS - CRUD OPERATIONS")

account_id = None
if token:
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create Account
    try:
        resp = requests.post(f"{BASE_URL}/accounts", 
            json={
                "name": "Test Checking",
                "account_type": "checking",
                "currency": "USD",
                "initial_balance": 1000
            },
            headers=headers
        )
        test("Create Account", resp.status_code == 200, f"Status: {resp.status_code}")
        if resp.status_code == 200:
            data = resp.json()
            account_id = data.get('id')
            test("Account ID recibido", bool(account_id))
    except Exception as e:
        test("Create Account", False, str(e))

    # Get Accounts
    try:
        resp = requests.get(f"{BASE_URL}/accounts", headers=headers)
        test("Get Accounts", resp.status_code == 200, f"Status: {resp.status_code}")
        if resp.status_code == 200:
            accounts = resp.json()
            test("Accounts es lista", isinstance(accounts, list))
            test("Almenos 1 cuenta", len(accounts) > 0, f"Encontradas: {len(accounts)}")
    except Exception as e:
        test("Get Accounts", False, str(e))

    # Update Account
    if account_id:
        try:
            resp = requests.put(f"{BASE_URL}/accounts/{account_id}",
                json={"name": "Updated Checking", "current_balance": 1500},
                headers=headers
            )
            test("Update Account", resp.status_code == 200, f"Status: {resp.status_code}")
        except Exception as e:
            test("Update Account", False, str(e))

# ==========================================
# TEST 3: CATEGORÍAS
# ==========================================
section("3. CATEGORÍAS - CRUD OPERATIONS")

category_id = None
if token:
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create Category
    try:
        resp = requests.post(f"{BASE_URL}/categories",
            json={
                "name": "Test Spending",
                "category_type": "expense",
                "icon": "fa-shopping-bag",
                "color": "#FF5722"
            },
            headers=headers
        )
        test("Create Category", resp.status_code == 200, f"Status: {resp.status_code}")
        if resp.status_code == 200:
            data = resp.json()
            category_id = data.get('id')
            test("Category ID recibido", bool(category_id))
    except Exception as e:
        test("Create Category", False, str(e))

    # Get Categories
    try:
        resp = requests.get(f"{BASE_URL}/categories", headers=headers)
        test("Get Categories", resp.status_code == 200, f"Status: {resp.status_code}")
        if resp.status_code == 200:
            categories = resp.json()
            test("Categories es lista", isinstance(categories, list))
            test("Almenos 1 categoría", len(categories) > 0)
    except Exception as e:
        test("Get Categories", False, str(e))

    # Suggest Category with AI
    try:
        resp = requests.post(f"{BASE_URL}/categories/suggest",
            json={
                "description": "Gasté en supermercado",
                "type": "expense",
                "language": "es"
            },
            headers=headers
        )
        test("Suggest Category AI", resp.status_code == 200, f"Status: {resp.status_code}")
    except Exception as e:
        test("Suggest Category AI", False, str(e))

# ==========================================
# TEST 4: TRANSACCIONES
# ==========================================
section("4. TRANSACCIONES - CRUD OPERATIONS")

transaction_id = None
if token and account_id and category_id:
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create Transaction
    try:
        resp = requests.post(f"{BASE_URL}/transactions",
            json={
                "account_id": account_id,
                "category_id": category_id,
                "transaction_type": "expense",
                "amount": 50.00,
                "description": "Test expense",
                "transaction_date": datetime.now().isoformat()
            },
            headers=headers
        )
        test("Create Transaction", resp.status_code == 200, f"Status: {resp.status_code}")
        if resp.status_code == 200:
            data = resp.json()
            transaction_id = data.get('id')
            test("Transaction ID recibido", bool(transaction_id))
    except Exception as e:
        test("Create Transaction", False, str(e))

    # Get Transactions
    try:
        resp = requests.get(f"{BASE_URL}/transactions", headers=headers)
        test("Get Transactions", resp.status_code == 200, f"Status: {resp.status_code}")
        if resp.status_code == 200:
            transactions = resp.json()
            test("Transactions es dict o lista", isinstance(transactions, (dict, list)))
    except Exception as e:
        test("Get Transactions", False, str(e))

    # Update Transaction
    if transaction_id:
        try:
            resp = requests.put(f"{BASE_URL}/transactions/{transaction_id}",
                json={"amount": 75.00, "description": "Updated expense"},
                headers=headers
            )
            test("Update Transaction", resp.status_code == 200, f"Status: {resp.status_code}")
        except Exception as e:
            test("Update Transaction", False, str(e))

# ==========================================
# TEST 5: CHAT & IA
# ==========================================
section("5. CHAT & IA - INITIALIZATION & CURRENCY")

if token:
    headers = {"Authorization": f"Bearer {token}"}
    
    # Init Chat
    try:
        resp = requests.post(f"{BASE_URL}/chat/init", headers=headers)
        test("Init Chat", resp.status_code == 200, f"Status: {resp.status_code}")
        if resp.status_code == 200:
            data = resp.json()
            test("Devuelve initialized", 'initialized' in data)
            test("Devuelve message", 'message' in data)
    except Exception as e:
        test("Init Chat", False, str(e))

    # Set Currency
    try:
        resp = requests.post(f"{BASE_URL}/chat/set-currency",
            json={"currency": "COP"},
            headers=headers
        )
        test("Set Currency", resp.status_code == 200, f"Status: {resp.status_code}")
    except Exception as e:
        test("Set Currency", False, str(e))

    # Send Chat Message
    try:
        resp = requests.post(f"{BASE_URL}/chat/send",
            json={"content": "Gasté 50.000 en supermercado"},
            headers=headers
        )
        test("Send Chat Message", resp.status_code == 200, f"Status: {resp.status_code}")
        if resp.status_code == 200:
            data = resp.json()
            test("Devuelve assistant_message", 'assistant_message' in data)
    except Exception as e:
        test("Send Chat Message", False, str(e))

    # Get Chat Messages
    try:
        resp = requests.get(f"{BASE_URL}/chat/messages", headers=headers)
        test("Get Chat Messages", resp.status_code == 200, f"Status: {resp.status_code}")
    except Exception as e:
        test("Get Chat Messages", False, str(e))

# ==========================================
# TEST 6: CONTROL COMMANDS (ChatOps)
# ==========================================
section("6. COMANDOS DE CONTROL - DELETE & RESET")

if token and account_id:
    headers = {"Authorization": f"Bearer {token}"}
    
    # Send command (should not execute without confirmation)
    try:
        resp = requests.post(f"{BASE_URL}/chat/send",
            json={"content": "Elimina todas mis transacciones"},
            headers=headers
        )
        test("Envía comando (sin ejecutar)", resp.status_code == 200)
        if resp.status_code == 200:
            data = resp.json()
            test("Solicita confirmación", 'pending_action' in data or 'CONFIRMAR' in data.get('assistant_message', ''))
    except Exception as e:
        test("Envía comando", False, str(e))

# ==========================================
# RESUMEN
# ==========================================
print(f"\n{GREEN}{'='*60}{RESET}")
print(f"{GREEN}PRUEBAS COMPLETADAS{RESET}")
print(f"{GREEN}{'='*60}{RESET}\n")
