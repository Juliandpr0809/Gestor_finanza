import requests
import time
import json
from datetime import datetime

BASE_URL = "http://localhost:5000"
timestamp = int(datetime.now().timestamp())
USERNAME = f"test_edit_{timestamp}"
EMAIL = f"test_edit_{timestamp}@example.com"
PASSWORD = "password123"

def log(msg):
    print(f"[TEST] {msg}")

def run_test():
    with requests.Session() as session:
        # Register
        log("Registering user...")
        res = session.post(f"{BASE_URL}/api/auth/register", json={
            "username": USERNAME, "email": EMAIL, "password": PASSWORD
        })
        if res.status_code != 201:
            log(f"Registration failed: {res.text}")
            return
            
        token = res.json().get('access_token')
        headers = {'Authorization': f'Bearer {token}'}
        
        # Init Chat
        log("Initializing Chat...")
        session.post(f"{BASE_URL}/api/chat/set-currency", json={"currency": "COP"}, headers=headers)
        
        # 1. Create Transaction
        log("Sending: Gasté 100 en error")
        res = session.post(f"{BASE_URL}/api/chat/send", json={"content": "Gasté 100 en error"}, headers=headers)
        if res.status_code != 201:
            log(f"Failed to create transaction: {res.text}")
            return
            
        # 2. Modify Previous
        log("Sending: Corrige la anterior, monto 50")
        res = session.post(f"{BASE_URL}/api/chat/send", json={"content": "Corrige la anterior, monto 50"}, headers=headers)
        print(f"Response: {res.text}")
        
        # 3. Verify
        res = session.get(f"{BASE_URL}/api/transactions", headers=headers)
        txs = res.json()
        if len(txs) > 0:
            last_tx = txs[-1]
            log(f"Last Transaction: {last_tx['description']} - {last_tx['amount']}")
            if last_tx['amount'] == 50.0:
                log("✅ TEST PASSED: Amount updated to 50")
            else:
                log("❌ TEST FAILED: Amount is not 50")
        else:
            log("❌ No transactions found")

if __name__ == "__main__":
    run_test()
