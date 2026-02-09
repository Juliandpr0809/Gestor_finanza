@echo off
REM Script para inicializar Git y hacer commit inicial

echo.
echo ================================
echo    Git Repository Initialization
echo ================================
echo.

REM Verificar si git está disponible
git --version >nul 2>&1
if errorlevel 1 (
    echo ✗ Git no está instalado o no está en PATH
    echo Por favor instala Git desde: https://git-scm.com/
    pause
    exit /b 1
)

REM Verificar si git ya está inicializado
if exist .git (
    echo ✓ Git ya está inicializado
) else (
    echo 🔧 Inicializando repositorio Git...
    git init
    if errorlevel 1 (
        echo ✗ Error al inicializar Git
        pause
        exit /b 1
    )
    echo ✓ Repositorio Git inicializado
)

echo.
echo ✓ Configurando Git...
git config user.email "dev@financeflow.local"
git config user.name "FinanceFlow Developer"
echo ✓ Configuración Git establecida

echo.
echo 📝 Agregando archivos...
git add .

echo.
echo 📊 Archivos a ser commiteados:
git status --short

echo.
echo 💾 Haciendo commit inicial...
git commit -m "Initial commit: Project structure and organization - Added comprehensive documentation - Organized project structure - Added .gitignore with proper patterns - Added LICENSE (MIT) - Moved test and utility files appropriately - Project ready for development and production"

if errorlevel 1 (
    echo ✗ Error al hacer commit
    pause
    exit /b 1
)

echo.
echo ✅ Repositorio inicializado correctamente!
echo.
echo 📌 Próximos pasos:
echo    1. Configurar remoto: git remote add origin https://github.com/usuario/Gestor_finansas.git
echo    2. Subir a GitHub: git push -u origin master
echo    3. Ver historial: git log --oneline
echo.
pause
