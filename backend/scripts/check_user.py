from app import create_app
from models import User, db
from werkzeug.security import generate_password_hash, check_password_hash

app = create_app()

with app.app_context():
    user = User.query.filter_by(email='demo@demo.com').first()
    
    if user:
        print(f"Usuario encontrado: {user.username}")
        print(f"Email: {user.email}")
        
        # Probar la contraseña actual
        test_password = 'demo1234'
        is_correct = check_password_hash(user.password_hash, test_password)
        print(f"Contraseña 'demo1234' es correcta: {is_correct}")
        
        if not is_correct:
            print("Actualizando contraseña...")
            user.password_hash = generate_password_hash('demo1234')
            db.session.commit()
            print("Contraseña actualizada a 'demo1234'")
    else:
        print("Usuario NO encontrado")
