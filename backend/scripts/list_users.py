from app import create_app
from models import User, db

app = create_app()

with app.app_context():
    print(f"Database URI: {app.config['SQLALCHEMY_DATABASE_URI']}")
    print("\nTodos los usuarios:")
    users = User.query.all()
    print(f"Total: {len(users)}")
    for u in users:
        print(f"  - ID: {u.id}, Username: {u.username}, Email: {u.email}")
