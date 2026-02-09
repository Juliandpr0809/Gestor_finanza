
import sys
import os
from sqlalchemy import inspect

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app import create_app, db

app = create_app()

with app.app_context():
    inspector = inspect(db.engine)
    tables = inspector.get_table_names()
    if 'account_balance_backups' in tables:
        print("VERIFICATION_SUCCESS: Table 'account_balance_backups' exists.")
    else:
        print("VERIFICATION_FAILURE: Table 'account_balance_backups' MISSING.")
