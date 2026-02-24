#!/usr/bin/env python3
"""
Script para validar que la PWA está correctamente configurada
Verifica manifest.json, service-worker.js y HTML meta tags
"""

import json
import sys
import os
from pathlib import Path
from urllib.parse import urlparse

def check_file_exists(file_path, name):
    """Verifica si un archivo existe"""
    if os.path.exists(file_path):
        print(f"✅ {name}: {file_path}")
        return True
    else:
        print(f"❌ {name}: NO ENCONTRADO - {file_path}")
        return False

def check_manifest(manifest_path):
    """Valida el manifest.json"""
    print("\n📋 Validando manifest.json...")
    
    try:
        with open(manifest_path, 'r', encoding='utf-8') as f:
            manifest = json.load(f)
        
        required_fields = ['name', 'short_name', 'display', 'icons']
        
        all_present = True
        for field in required_fields:
            if field in manifest:
                print(f"  ✅ {field}: {manifest.get(field)}")
            else:
                print(f"  ❌ {field}: FALTA")
                all_present = False
        
        # Verificaciones adicionales
        if manifest.get('display') != 'standalone':
            print(f"  ⚠️  display debería ser 'standalone', tiene: {manifest.get('display')}")
        
        if not manifest.get('start_url'):
            print(f"  ❌ start_url está vacío")
            all_present = False
        else:
            print(f"  ✅ start_url: {manifest.get('start_url')}")
        
        if manifest.get('icons'):
            print(f"  ✅ Tiene {len(manifest['icons'])} icono(s)")
        else:
            print(f"  ❌ No tiene iconos definidos")
            all_present = False
        
        if manifest.get('scope'):
            print(f"  ✅ scope: {manifest.get('scope')}")
        
        return all_present
        
    except json.JSONDecodeError as e:
        print(f"  ❌ JSON inválido: {e}")
        return False
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False

def check_service_worker(sw_path):
    """Valida el service-worker.js"""
    print("\n⚙️  Validando service-worker.js...")
    
    try:
        with open(sw_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        checks = {
            'self.addEventListener': 'Listeners registrados',
            'caches': 'API de caché',
            'CACHE_NAME': 'Cache name definido',
            'install': 'Evento install',
            'activate': 'Evento activate',
            'fetch': 'Evento fetch'
        }
        
        all_present = True
        for keyword, description in checks.items():
            if keyword in content:
                print(f"  ✅ {description}")
            else:
                print(f"  ❌ {description} - NO ENCONTRADO")
                all_present = False
        
        # Tamaño del archivo
        size = len(content)
        print(f"  📊 Tamaño: {size} bytes")
        
        return all_present
        
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False

def check_html_meta_tags(html_path):
    """Valida los meta tags necesarios para PWA en HTML"""
    print("\n📄 Validando meta tags en HTML...")
    
    try:
        with open(html_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        required_tags = {
            '<meta charset="UTF-8">': 'Charset UTF-8',
            'viewport': 'Viewport meta tag',
            'theme-color': 'Theme color',
            'apple-mobile-web-app-capable': 'Apple mobile web app capable',
            'manifest': 'Link al manifest.json',
            'service-worker': 'Registro del service worker'
        }
        
        all_present = True
        for tag, description in required_tags.items():
            if tag in content:
                print(f"  ✅ {description}")
            else:
                print(f"  ❌ {description} - NO ENCONTRADO")
                all_present = False
        
        return all_present
        
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False

def print_summary():
    """Imprime resumen de PWA deployment"""
    print("\n" + "="*60)

    print("📊 RESUMEN DE VALIDACIÓN PWA")
    print("="*60)
    
    print("""
    Para usar como app nativa en teléfono:

    1. ✅ Verifica que tu despliegue esté en HTTPS
       - Heroku: Automático
       - PythonAnywhere: Dashboard → Security → Force HTTPS
       - Otros: Añade SSL/TLS certificado

    2. ✅ Abre en Chrome del teléfono:
       - https://tu-dominio.com
       - ESPERA 3-5 segundos

    3. ✅ Cuando veas el popup "Instalar OrdenC":
       - Android: Toca "Instalar"
       - iPhone: Menú compartir → "Agregar a pantalla de inicio"

    4. ✅ La app aparecerá en tu pantalla de inicio

    Documentación completa:
    - docs/PWA_INSTALACION.md
    - docs/HTTPS_DEPLOYMENT.md
    """)
    
    print("="*60)

def main():
    """Función principal"""
    print("🔍 Validando configuración de PWA...")
    print("="*60)
    
    # Obtener ruta base
    current_dir = Path(__file__).parent.parent
    frontend_dir = current_dir / 'frontend'
    
    manifest_path = frontend_dir / 'manifest.json'
    sw_path = frontend_dir / 'service-worker.js'
    html_path = frontend_dir / 'html' / 'index.html'
    
    # Verificar archivos existen
    print("\n📁 Verificando archivos...")
    files_ok = True
    files_ok &= check_file_exists(str(manifest_path), "manifest.json")
    files_ok &= check_file_exists(str(sw_path), "service-worker.js")
    files_ok &= check_file_exists(str(html_path), "index.html")
    
    if not files_ok:
        print("\n❌ Faltan archivos críticos de PWA")
        return 1
    
    # Validar contenido
    manifest_ok = check_manifest(str(manifest_path))
    sw_ok = check_service_worker(str(sw_path))
    html_ok = check_html_meta_tags(str(html_path))
    
    # Resultado final
    print_summary()
    
    if manifest_ok and sw_ok and html_ok:
        print("\n✅ ¡PWA CORRECTAMENTE CONFIGURADA!")
        print("\n   Tu app está lista para instalar como aplicación nativa")
        print("   en teléfonos Android e iOS.\n")
        return 0
    else:
        print("\n⚠️  Algunas configuraciones necesitan ajustes")
        return 1

if __name__ == '__main__':
    sys.exit(main())
