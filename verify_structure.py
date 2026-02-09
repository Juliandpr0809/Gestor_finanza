#!/usr/bin/env python3
"""
Script de verificación de la estructura del proyecto
Comprueba que el proyecto esté correctamente organizado para producción
"""

import os
import sys
from pathlib import Path

def check_structure():
    """Verifica la estructura del proyecto"""
    
    print("\n" + "="*60)
    print("  VERIFICACIÓN DE ESTRUCTURA DEL PROYECTO")
    print("="*60 + "\n")
    
    project_root = Path(".")
    issues = []
    warnings = []
    success = []
    
    # Archivos requeridos en raíz
    required_files = {
        ".gitignore": "Configuración de Git",
        "README.md": "Documentación principal",
        "LICENSE": "Licencia del proyecto",
        "CONTRIBUTING.md": "Guía para contribuidores",
        "DEVELOPMENT.md": "Guía de desarrollo",
        "DEPLOYMENT.md": "Guía de despliegue",
        "CHANGELOG.md": "Registro de cambios",
        "PROJECT_STRUCTURE.md": "Estructura del proyecto",
    }
    
    print("📋 ARCHIVOS REQUERIDOS EN RAÍZ:\n")
    for file, description in required_files.items():
        if (project_root / file).exists():
            print(f"  ✓ {file:<20} - {description}")
            success.append(file)
        else:
            print(f"  ✗ {file:<20} - {description}")
            issues.append(f"Archivo faltante: {file}")
    
    # Directorios requeridos
    required_dirs = {
        "backend": "Backend Flask",
        "frontend": "Frontend PWA",
        "tests": "Tests de integración",
        "docs": "Documentación",
        ".venv": "Entorno virtual",
    }
    
    print("\n📁 DIRECTORIOS REQUERIDOS:\n")
    for dir_name, description in required_dirs.items():
        if (project_root / dir_name).is_dir():
            print(f"  ✓ {dir_name:<20} - {description}")
            success.append(dir_name)
        else:
            if dir_name == ".venv":
                warnings.append(f"Dirección opcional: {dir_name}")
                print(f"  ⚠ {dir_name:<20} - (Opcional, crear con 'python -m venv .venv')")
            else:
                print(f"  ✗ {dir_name:<20} - {description}")
                issues.append(f"Directorio faltante: {dir_name}")
    
    # Verificar backend
    print("\n🔹 ESTRUCTURA BACKEND:\n")
    backend_dirs = {
        "models": "Modelos de datos",
        "routes": "Endpoints API",
        "services": "Lógica de negocio",
        "schemas": "Validación",
        "utils": "Utilidades",
        "scripts": "Scripts de administración",
        "tests": "Tests unitarios",
        "migrations": "Migraciones BD",
    }
    
    for dir_name, description in backend_dirs.items():
        backend_path = project_root / "backend" / dir_name
        if backend_path.is_dir():
            print(f"  ✓ backend/{dir_name:<15} - {description}")
            success.append(f"backend/{dir_name}")
        else:
            warnings.append(f"Directorio no encontrado: backend/{dir_name}")
            print(f"  ⚠ backend/{dir_name:<15} - {description}")
    
    # Archivos en backend
    print("\n📄 ARCHIVOS PRINCIPALES BACKEND:\n")
    backend_files = {
        "app.py": "Aplicación Flask",
        "config.py": "Configuraciones",
        "requirements.txt": "Dependencias producción",
        "requirements-test.txt": "Dependencias desarrollo",
        ".env.example": "Template variables entorno",
    }
    
    for file, description in backend_files.items():
        if (project_root / "backend" / file).exists():
            print(f"  ✓ backend/{file:<25} - {description}")
            success.append(f"backend/{file}")
        else:
            warnings.append(f"Archivo no encontrado: backend/{file}")
            print(f"  ⚠ backend/{file:<25} - {description}")
    
    # Verificar tests no estén en raíz
    print("\n🧪 VERIFICACIÓN DE TESTS:\n")
    root_test_files = [
        "test_*.py",
        "*_test.py",
        "tests.py"
    ]
    
    test_files_in_root = []
    for pattern in root_test_files:
        if "*" in pattern:
            test_files_in_root.extend(project_root.glob(pattern))
    
    if not test_files_in_root:
        print("  ✓ No hay archivos de test en la raíz")
        success.append("Tests organizados")
    else:
        print(f"  ⚠ Encontrados {len(test_files_in_root)} archivo(s) de test en raíz:")
        for f in test_files_in_root:
            print(f"    - {f}")
            warnings.append(f"Test en raíz: {f}")
    
    # Verificar .gitignore
    print("\n🔒 VERIFICACIÓN DE SEGURIDAD:\n")
    gitignore_path = project_root / ".gitignore"
    if gitignore_path.exists():
        with open(gitignore_path) as f:
            content = f.read()
            
        important_patterns = [
            ".env",
            "*.db",
            "__pycache__",
            "*.pyc",
            ".venv",
            "instance/",
            ".vscode/",
            ".idea/"
        ]
        
        for pattern in important_patterns:
            if pattern in content:
                print(f"  ✓ .gitignore contiene: {pattern}")
                success.append(f"gitignore-{pattern}")
            else:
                warnings.append(f"Patrón faltante en .gitignore: {pattern}")
                print(f"  ⚠ .gitignore NO contiene: {pattern}")
    else:
        issues.append(".gitignore no encontrado")
        print("  ✗ .gitignore no encontrado")
    
    # Verificar archivos sensibles
    print("\n🔐 ARCHIVOS SENSIBLES:\n")
    sensitive_files = [
        ".env",
        "*.db",
        "*.sqlite",
        "*.pid"
    ]
    
    found_sensitive = False
    for pattern in sensitive_files:
        if "*" in pattern:
            matches = list(project_root.glob(pattern))
            if matches:
                found_sensitive = True
                for f in matches:
                    if f.name not in [".gitignore", "*.example"]:
                        print(f"  ⚠ Encontrado archivo sensible: {f}")
                        if f.suffix == ".db" or f.suffix == ".sqlite":
                            warnings.append(f"Base de datos en raíz: {f}")
                        elif f.name == ".env":
                            issues.append(f"ALERTA: .env en raíz, debe estar en .gitignore")
                        else:
                            warnings.append(f"Archivo sensible: {f}")
    
    if not found_sensitive:
        print("  ✓ No hay archivos sensibles en la raíz")
        success.append("Sin archivos sensibles")
    
    # Resumen
    print("\n" + "="*60)
    print("  RESUMEN")
    print("="*60)
    
    print(f"\n✓ Éxitos: {len(success)}")
    print(f"⚠ Advertencias: {len(warnings)}")
    print(f"✗ Problemas: {len(issues)}")
    
    if warnings:
        print("\n⚠️  ADVERTENCIAS:")
        for warning in warnings:
            print(f"  • {warning}")
    
    if issues:
        print("\n❌ PROBLEMAS ENCONTRADOS:")
        for issue in issues:
            print(f"  • {issue}")
        return False
    
    print("\n" + "="*60)
    print("  ✅ PROYECTO ESTRUCTURADO CORRECTAMENTE")
    print("="*60)
    print("\nTu proyecto está listo para:")
    print("  • Desarrollo con estándares profesionales")
    print("  • Subir a GitHub/GitLab")
    print("  • Despliegue a producción")
    print("  • Colaboración en equipo")
    print("\nPróximos pasos:")
    print("  1. Inicializar Git: git init")
    print("  2. Hacer primer commit: git add . && git commit -m 'Initial commit'")
    print("  3. Conectar remoto: git remote add origin <url>")
    print("  4. Subir código: git push -u origin main")
    print("\n" + "="*60 + "\n")
    
    return True

if __name__ == "__main__":
    success = check_structure()
    sys.exit(0 if success else 1)
