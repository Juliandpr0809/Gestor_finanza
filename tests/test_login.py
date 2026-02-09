"""Script para probar login y verificar usuarios"""
from app import create_app
from models import db, User
from werkzeug.security import check_password_hash

app = create_app()

with app.app_context():
    print("=" * 60)
    print("USUARIOS EN LA BASE DE DATOS")
    print("=" * 60)
    
    users = User.query.all()
    
    if not users:
        print("⚠️  No hay usuarios registrados")
    else:
        for user in users:
            print(f"\n👤 Usuario ID: {user.id}")
            print(f"   Username: {user.username}")
            print(f"   Email: {user.email}")
            print(f"   Password Hash: {user.password_hash[:50]}...")
    
    print("\n" + "=" * 60)
    print("PRUEBA DE LOGIN")
    print("=" * 60)
    
    # Probar con el usuario que conocemos
    test_email = "juliandpr0809@gmai.com"
    test_password = input(f"\nIngresa la contraseña para {test_email}: ")
    
    user = User.query.filter_by(email=test_email).first()
    
    if user:
        print(f"\n✅ Usuario encontrado: {user.username}")
        
        # Verificar contraseña
        if check_password_hash(user.password_hash, test_password):
            print("✅ Contraseña CORRECTA")
        else:
            print("❌ Contraseña INCORRECTA")
            
            # Intentar con contraseñas comunes
            print("\nProbando contraseñas comunes...")
            common_passwords = ['password', 'admin', '123456', 'test123', 'demo']
            for pwd in common_passwords:
                if check_password_hash(user.password_hash, pwd):
                    print(f"✅ La contraseña es: {pwd}")
                    break
    else:
        print(f"❌ Usuario no encontrado con email: {test_email}")
