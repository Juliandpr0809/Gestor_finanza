#!/usr/bin/env python
"""
Script para aplicar migraciones
"""
import sys
import os

# Configurar encoding
os.environ['PYTHONIOENCODING'] = 'utf-8'

# Agregar el directorio backend al path
backend_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend')
sys.path.insert(0, backend_path)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Cambiar al directorio backend para que encuentre las migraciones
os.chdir(backend_path)

from app import create_app, db
from flask_migrate import upgrade

app = create_app('development')

with app.app_context():
    print("Aplicando migraciones...")
    try:
        upgrade()
        print("Migraciones aplicadas exitosamente!")
    except Exception as e:
        print(f"Error al aplicar migraciones: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
