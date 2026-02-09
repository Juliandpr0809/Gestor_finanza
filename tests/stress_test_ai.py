import requests
import json
import time

BASE_URL = "http://localhost:5000"
TEST_USER = {
    "username": f"TestUser_{int(time.time())}",
    "email": f"tester_{int(time.time())}@test.com",
    "password": "password123"
}

def log(msg):
    print(f"[TEST] {msg}")

def run_tests():
    session = requests.Session()
    
    # 1. Register
    log(f"Registering user {TEST_USER['email']}...")
    try:
        res = session.post(f"{BASE_URL}/api/auth/register", json=TEST_USER)
        if res.status_code == 201:
            log("Registration successful.")
            token = res.json().get('access_token')
        else:
            log(f"Registration failed: {res.text}")
            # Try login
            res = session.post(f"{BASE_URL}/api/auth/login", json=TEST_USER)
            if res.status_code == 200:
                log("Login successful.")
                token = res.json().get('access_token')
            else:
                log("Login failed. Aborting.")
                return

        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        
        # 2. Init Chat (Set Currency)
        log("Initializing Chat (Setting Currency to COP)...")
        session.post(f"{BASE_URL}/api/chat/set-currency", json={"currency": "COP"}, headers=headers)
        
        # 3. Test Cases (Updated for NLP Fixes)
        test_cases = [
            "Gasté 50000 ayer en taxi",        # Date Test
            "Gasté 10 USD en suscripción",     # Currency Test (should convert to ~40k)
            "Gasté 50 en pan",                 # Base for Context
            "Y 20 en leche",                   # Context Test (should inherit expense)
            "Compré 3 manzanas",               # Ambiguity Test (should NOT pass)
            "Crear cuenta Ahorros con 100000"  # Control Command
        ]
        
        for msg in test_cases:
            log(f"\nScanning: '{msg}'")
            res = session.post(f"{BASE_URL}/api/chat/send", json={"content": msg}, headers=headers)
            if res.status_code == 201:
                data = res.json()
                ai_reply = data['assistant_message']['content']
                log(f"AI Response: {ai_reply[:200]}...") 
            else:
                log(f"Error ({res.status_code}): {res.text}")
            time.sleep(1)
            
    except Exception as e:
        log(f"Exception: {e}")

if __name__ == "__main__":
    run_tests()
