
import sys
import os

# Add backend to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))

from services.groq_service import suggest_category_with_ai
from dotenv import load_dotenv

load_dotenv()

# Spontaneous and unique test cases
test_cases = [
    # Standard
    ("Uber a la oficina", "expense"),
    ("Compra en D1", "expense"),
    # Specific / Niche
    ("Comida para el gato de la vecina", "expense"),
    ("Suscripción de Netflix", "expense"),
    ("Spotify premium", "expense"),
    ("Corte de cabello", "expense"),
    # Tech / Work
    ("Mouse ergonómico", "expense"),
    ("Hosting del servidor", "expense"),
    # Fun / Social
    ("Polas con los amigos", "expense"),
    ("Salida a cine", "expense"),
    
    # Income
    ("Pago de nómina", "income"),
    ("Venta de bicicleta vieja", "income"),
    ("Devolución de dinero prestado", "income")
]

# Mock user categories (Simulating a user with these existing cats)
mock_user_categories_expense = [
    'ComidaAndFarts', 'Transporte', 'Mascotas', 'Tech', 'Salud', 'Entretenimiento', 'Vicios', 'Otros'
]
mock_user_categories_income = [
    'Salario', 'Negocios Turbios', 'Ventas', 'Otros'
]

print("-" * 60)
print(f"{'INPUT':<35} | {'PERCEIVED TYPE':<10} | {'AI SUGGESTION':<20}")
print("-" * 60)

for desc, tx_type in test_cases:
    cats = mock_user_categories_expense if tx_type == 'expense' else mock_user_categories_income
    
    # Call the actual service
    result = suggest_category_with_ai(desc, tx_type, 'es', available_categories=cats)
    
    category = result.get('category', 'None')
    print(f"{desc:<35} | {tx_type:<10} | {category}")

print("-" * 60)
