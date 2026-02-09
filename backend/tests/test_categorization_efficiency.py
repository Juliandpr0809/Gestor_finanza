import requests
import time
import random
import json
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:5000"
timestamp = int(time.time())
TEST_USER = {
    "username": f"BenchUser_{timestamp}",
    "email": f"bench_{timestamp}@test.com",
    "password": "password123"
}

# Transaction Dataset (Description, Amount, Expected Category Keyword, Type)
# Using keywords because exact category names might vary, we will match loosely.
TEST_DATA = [
    ("Compra en Supermercado Exito", 150000, "Comida", "expense"),
    ("Mercado mensual Carulla", 450000, "Comida", "expense"),
    ("Almuerzo en El Corral", 35000, "Comida", "expense"),
    ("Cena en Crepes & Waffles", 60000, "Comida", "expense"),
    ("Uber a la oficina", 15000, "Transporte", "expense"),
    ("Taxi al aeropuerto", 45000, "Transporte", "expense"),
    ("Recarga tarjeta TuLlave", 20000, "Transporte", "expense"),
    ("Tanqueada de gasolina", 80000, "Transporte", "expense"),
    ("Pago arriendo apartamento", 1200000, "Vivienda", "expense"),
    ("Factura de luz Enel", 85000, "Servicios", "expense"),
    ("Factura de agua Acueducto", 45000, "Servicios", "expense"),
    ("Internet y TV Claro", 120000, "Servicios", "expense"),
    ("Suscripción Netflix", 18000, "Entretenimiento", "expense"),
    ("Suscripción Spotify", 15000, "Entretenimiento", "expense"),
    ("Entradas a Cine Colombia", 40000, "Entretenimiento", "expense"),
    ("Juego en Steam", 120000, "Entretenimiento", "expense"),
    ("Medicamentos Cruz Verde", 45000, "Salud", "expense"),
    ("Cita médica prepagada", 35000, "Salud", "expense"),
    ("Mensualidad gimnasio SmartFit", 80000, "Salud", "expense"),
    ("Libro técnico Amazon", 150000, "Educación", "expense"),
    ("Curso de Python online", 450000, "Educación", "expense"),
    ("Pago de nómina quincenal", 2500000, "Ingresos", "income"),
    ("Transferencia de cliente freelance", 800000, "Ingresos", "income"),
    ("Venta de bicicleta vieja", 350000, "Otros", "income"),
    ("Regalo de cumpleaños abuela", 100000, "Otros", "income"),
    ("Compra jeans Levi's", 180000, "Ropa", "expense"),
    ("Zapatillas Nike", 320000, "Ropa", "expense"),
    ("Cervezas con amigos", 50000, "Entretenimiento", "expense"),
    ("Mantenimiento del carro", 450000, "Transporte", "expense"),
    ("Pago administración edificio", 250000, "Vivienda", "expense"),
]

# Generate more random variations
VARIATIONS = [
    ("Hamburguesa", "Comida"), ("Pizza", "Comida"), ("Sushi", "Comida"),
    ("Bus", "Transporte"), ("Metro", "Transporte"), ("Gasolina", "Transporte"),
    ("Luz", "Servicios"), ("Agua", "Servicios"), ("Gas", "Servicios"),
    ("Cine", "Entretenimiento"), ("Teatro", "Entretenimiento"), ("Concierto", "Entretenimiento"),
    ("Doctor", "Salud"), ("Farmacia", "Salud"), ("Dentista", "Salud"),
    ("Universidad", "Educación"), ("Curso", "Educación"), ("Taller", "Educación"),
    ("Camisa", "Ropa"), ("Zapatos", "Ropa"), ("Chaqueta", "Ropa"),
    ("Salario", "Ingresos"), ("Bono", "Ingresos"), ("Dividendo", "Ingresos")
]

for _ in range(20): # Add 20 more random simple ones
    item = random.choice(VARIATIONS)
    amount = random.randint(10, 500) * 1000
    expected = item[1]
    t_type = "income" if expected == "Ingresos" else "expense"
    TEST_DATA.append((f"{item[0]} random", amount, expected, t_type))

class CategorizationBenchmark:
    def __init__(self):
        self.session = requests.Session()
        self.token = None
        self.accounts = []
        self.categories = [] # List of dicts {id, name, type}
        self.results = {
            "ai": {"correct": 0, "total": 0, "time_ms": []},
            "manual": {"correct": 0, "total": 0, "time_ms": []}
        }
        self.results['smart'] = {"correct": 0, "total": 0, "time_ms": []}
        self.errors = []

    def log(self, msg):
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")

    def setup(self):
        self.log("Setting up environment...")
        
        # 1. Register
        res = self.session.post(f"{BASE_URL}/api/auth/register", json=TEST_USER)
        if res.status_code != 201:
            # Try login if exists
            res = self.session.post(f"{BASE_URL}/api/auth/login", json=TEST_USER)
        
        if res.status_code not in [200, 201]:
            raise Exception(f"Auth failed: {res.text}")
            
        self.token = res.json()['access_token']
        self.session.headers.update({"Authorization": f"Bearer {self.token}"})
        self.log(f"Logged in as {TEST_USER['username']}")

        # 2. Get Accounts (Create if none)
        res = self.session.get(f"{BASE_URL}/api/accounts")
        accounts_data = res.json()
        if not accounts_data:
            # Create default account
            res_create = self.session.post(f"{BASE_URL}/api/accounts", json={"name": "Bank", "account_type": "bank", "currency": "COP", "initial_balance": 10000000})
            if res_create.status_code != 201:
                self.log(f"Failed to create account: {res_create.text}")
            res = self.session.get(f"{BASE_URL}/api/accounts")
            accounts_data = res.json()
        
        self.accounts = accounts_data
        self.log(f"Loaded {len(self.accounts)} accounts.")

        # 3. Get Categories
        res = self.session.get(f"{BASE_URL}/api/categories")
        self.categories = res.json()
        self.log(f"Loaded {len(self.categories)} categories.")
        
        # Initialize Chat
        self.session.post(f"{BASE_URL}/api/chat/set-currency", json={"currency": "COP"})

    def get_category_id(self, keyword, t_type):
        # Simple fuzzy match or substring
        keyword_lower = keyword.lower()
        
        # Priority 1: Exact type match and name match
        for cat in self.categories:
            if cat['type'] == t_type and keyword_lower in cat['name'].lower():
                return cat['id'], cat['name']
        
        # Priority 2: Name match only
        for cat in self.categories:
            if keyword_lower in cat['name'].lower():
                return cat['id'], cat['name']
                
        # Fallback: Return first of type
        for cat in self.categories:
            if cat['type'] == t_type:
                return cat['id'], cat['name']
        
        return self.categories[0]['id'], self.categories[0]['name']

    def test_ai_chat(self):
        self.log(f"\n--- Testing AI Chat Categorization ({len(TEST_DATA)} items) ---")
        
        for desc, amount, expected_cat, t_type in TEST_DATA:
            message = f"Gaste {amount} en {desc}" if t_type == 'expense' else f"Recibí {amount} por {desc}"
            
            start_time = time.time()
            res = self.session.post(f"{BASE_URL}/api/chat/send", json={"content": message})
            duration_ms = (time.time() - start_time) * 1000
            
            if res.status_code == 201:
                # To check accuracy, we fetch the latest transaction
                # Wait a bit for async DB? Usually sync.
                tx_res = self.session.get(f"{BASE_URL}/api/transactions?per_page=1")
                recent_tx = tx_res.json()['transactions'][0]
                
                actual_cat = recent_tx['category_name']
                
                # Check match
                is_correct = expected_cat.lower() in actual_cat.lower() or actual_cat.lower() in expected_cat.lower()
                
                self.results['ai']['total'] += 1
                self.results['ai']['time_ms'].append(duration_ms)
                
                if is_correct:
                    self.results['ai']['correct'] += 1
                    status = "PASS"
                else:
                    status = "FAIL"
                    self.errors.append(f"[AI] Expected '{expected_cat}' for '{desc}', got '{actual_cat}'")
                
                print(f"[{status}] '{desc}' -> {actual_cat} ({int(duration_ms)}ms)")
            else:
                self.log(f"Error calling Chat: {res.text}")

    def test_manual_entry(self):
        self.log(f"\n--- Testing Manual Entry Efficiency ({len(TEST_DATA)} items) ---")
        
        # In manual mode, we are the human so we pick the right category.
        # We are measuring the *system's* speed to process it, and verifying 100% accuracy logic theoretically.
        
        account_id = self.accounts[0]['id']
        
        for desc, amount, expected_cat, t_type in TEST_DATA:
            cat_id, cat_name = self.get_category_id(expected_cat, t_type)
            
            payload = {
                "account_id": account_id,
                "category_id": cat_id,
                "amount": amount,
                "type": t_type,
                "description": desc,
                "date": datetime.now().isoformat()
            }
            
            start_time = time.time()
            res = self.session.post(f"{BASE_URL}/api/transactions", json=payload)
            duration_ms = (time.time() - start_time) * 1000
            
            if res.status_code == 201:
                # Verify
                tx_res = self.session.get(f"{BASE_URL}/api/transactions?per_page=1")
                recent_tx = tx_res.json()['transactions'][0]
                actual_cat = recent_tx['category_name']
                
                is_correct = cat_name == actual_cat
                
                self.results['manual']['total'] += 1
                self.results['manual']['time_ms'].append(duration_ms)
                
                if is_correct:
                    self.results['manual']['correct'] += 1
                else:
                    self.errors.append(f"[MANUAL] Mismatch? Sent {cat_name}, got {actual_cat}")
                    
                print(f"[MANUAL] '{desc}' -> {actual_cat} ({int(duration_ms)}ms)")
            else:
                self.log(f"Error creating transaction: {res.text}")

    def test_smart_manual_suggestion(self):
        self.log(f"\n--- Testing Smart Manual Suggestion API ({len(TEST_DATA)} items) ---")
        
        for desc, amount, expected_cat, t_type in TEST_DATA:
            start_time = time.time()
            res = self.session.post(f"{BASE_URL}/api/categories/suggest", json={
                "description": desc,
                "type": t_type
            })
            duration_ms = (time.time() - start_time) * 1000
            
            if res.status_code == 200:
                data = res.json()
                suggested_cat = data.get('category')
                confidence = data.get('confidence', 0)
                source = data.get('source', 'unknown')
                
                # Check match
                is_correct = False
                if suggested_cat:
                    is_correct = expected_cat.lower() in suggested_cat.lower() or suggested_cat.lower() in expected_cat.lower()
                
                self.results['smart']['total'] += 1
                self.results['smart']['time_ms'].append(duration_ms)
                
                if is_correct:
                    self.results['smart']['correct'] += 1
                    status = "PASS"
                else:
                    self.errors.append(f"[SMART] Expected '{expected_cat}' for '{desc}', got '{suggested_cat}' (Source: {source})")
                    status = "FAIL"
                    
                print(f"[{status}] '{desc}' -> {suggested_cat} ({int(duration_ms)}ms) [{source}]")
            else:
                self.log(f"Error calling Suggest API: {res.text}")


    def print_report(self):
        print("\n" + "="*50)
        print("          CATEGORIZATION EFFICIENCY REPORT          ")
        print("="*50)
        
        # AI Stats
        ai_total = self.results['ai']['total']
        ai_correct = self.results['ai']['correct']
        ai_acc = (ai_correct / ai_total * 100) if ai_total > 0 else 0
        ai_avg_time = sum(self.results['ai']['time_ms']) / ai_total if ai_total > 0 else 0
        
        print(f"\n[AI CHAT]")
        print(f"Transactions: {ai_total}")
        print(f"Accuracy:     {ai_acc:.1f}% ({ai_correct}/{ai_total})")
        print(f"Avg Latency:  {ai_avg_time:.0f} ms")
        
        # Manual Stats
        man_total = self.results['manual']['total']
        man_correct = self.results['manual']['correct']
        man_acc = (man_correct / man_total * 100) if man_total > 0 else 0
        man_avg_time = sum(self.results['manual']['time_ms']) / man_total if man_total > 0 else 0
        
        print(f"\n[MANUAL API]")
        print(f"Transactions: {man_total}")
        print(f"Accuracy:     {man_acc:.1f}% (Old Baseline)")
        print(f"Avg Latency:  {man_avg_time:.0f} ms")
        
        # Smart Manual Stats
        smart_total = self.results['smart']['total']
        smart_correct = self.results['smart']['correct']
        smart_acc = (smart_correct / smart_total * 100) if smart_total > 0 else 0
        smart_avg_time = sum(self.results['smart']['time_ms']) / smart_total if smart_total > 0 else 0
        
        print(f"\n[SMART PREDICTION API]")
        print(f"Transactions: {smart_total}")
        print(f"Accuracy:     {smart_acc:.1f}% (New Manual Flow)")
        print(f"Avg Latency:  {smart_avg_time:.0f} ms")
        
        print("\n[COMPARISON]")
        if smart_avg_time > 0 and ai_avg_time > 0:
            speedup = ai_avg_time / smart_avg_time
            print(f"Smart Prediction is {speedup:.1f}x faster than Chat")
        
        if self.errors:
            print("\n[AI MISCLASSIFICATIONS & ERRORS]")
            for err in self.errors:
                print(f" - {err}")
        
        print("="*50)

if __name__ == "__main__":
    benchmark = CategorizationBenchmark()
    try:
        benchmark.setup()
        benchmark.test_ai_chat()
        benchmark.test_manual_entry()
        benchmark.test_smart_manual_suggestion()
        benchmark.print_report()
    except Exception as e:
        print(f"\nCRITICAL ERROR: {e}")
