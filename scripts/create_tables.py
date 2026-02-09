
import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app import create_app, db
from models import AccountBalanceBackup

app = create_app()

with app.app_context():
    print("Creating missing tables...")
    try:
        db.create_all()
        print("✅ Tables created successfully.")
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
