#!/bin/bash
# Script para inicializar Git y hacer commit inicial

cd "$(dirname "$0")"

echo "🔧 Inicializando repositorio Git..."

# Verificar si git ya está inicializado
if [ -d .git ]; then
    echo "✓ Git ya está inicializado"
else
    git init
    echo "✓ Repositorio Git inicializado"
fi

# Configurar nombre y email (cambiar según sea necesario)
git config user.email "dev@financeflow.local" || git config --global user.email "dev@financeflow.local"
git config user.name "FinanceFlow Developer" || git config --global user.name "FinanceFlow Developer"

echo "✓ Configuración Git establecida"

# Añadir archivos
echo "📝 Agregando archivos..."
git add .

# Mostrar estatus
echo ""
echo "📊 Archivos a ser commiteados:"
git status --short

# Hacer commit inicial
echo ""
echo "💾 Haciendo commit inicial..."
git commit -m "Initial commit: Project structure and organization

- Added comprehensive documentation (README, CONTRIBUTING, DEPLOYMENT, DEVELOPMENT)
- Organized project structure (backend, frontend, tests, docs)
- Added .gitignore with proper patterns
- Added LICENSE (MIT)
- Added CHANGELOG and PROJECT_STRUCTURE
- Moved test files to tests/ directory
- Moved utility scripts to backend/scripts/
- Moved examples to docs/
- Added .env.example with configuration template
- Project ready for development and production"

echo ""
echo "✅ Repositorio inicializado y commit inicial completado!"
echo ""
echo "📌 Próximos pasos:"
echo "1. Configurar remoto: git remote add origin https://github.com/usuario/Gestor_finansas.git"
echo "2. Subir a GitHub: git push -u origin master"
echo ""
echo "Para ver el historial: git log --oneline"
