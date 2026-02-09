"""Script para verificar el token JWT del usuario"""
import sys
from app import create_app
from models import db, User
from utils.jwt_utils import generate_access_token

app = create_app()

with app.app_context():
    # Buscar el usuario juliandpr0809
    user = User.query.filter_by(email='juliandpr0809@gmai.com').first()
    
    if user:
        print(f"Usuario encontrado:")
        print(f"  ID: {user.id}")
        print(f"  Email: {user.email}")
        print(f"  Username: {user.username}")
        
        # Generar nuevo token
        token = generate_access_token(user.id, user.email)
        print(f"\n🔑 Token JWT generado:")
        print(token)
        print("\n⚠️ Copia este token y actualiza tu localStorage en el navegador:")
        print("localStorage.setItem('token', '" + token + "');")
    else:
        print("Usuario no encontrado")
