#!/bin/bash

# Script para agregar i18n a todas las páginas HTML
# Ejecutar desde la carpeta raíz del proyecto

echo "Agregando sistema de idiomas a todas las páginas..."

# Páginas a actualizar
pages=(
    "frontend/html/accounts.html"
    "frontend/html/transactions.html"
    "frontend/html/reports.html"
    "frontend/html/new-transaction.html"
    "frontend/html/scan-receipt.html"
    "frontend/html/voice-input.html"
)

for page in "${pages[@]}"; do
    if [ -f "$page" ]; then
        echo "Procesando $page..."
        
        # 1. Agregar CSS de lang-selector si no existe
        if ! grep -q "lang-selector.css" "$page"; then
            sed -i 's/<\/head>/<link rel="stylesheet" href="..\/css\/lang-selector.css">\n<\/head>/' "$page"
        fi
        
        # 2. Agregar script i18n.js si no existe
        if ! grep -q "i18n.js" "$page"; then
            sed -i 's/<script src="..\/js\/api.js/<script src="..\/js\/i18n.js"><\/script>\n    <script src="..\/js\/api.js/' "$page"
        fi
        
        # 3. Cambiar "Dashboard" por data-i18n en nav
        sed -i 's/>Dashboard</>Panel<\/a>/g' "$page"
        sed -i 's/class="header-nav-item active">/class="header-nav-item active" data-i18n="Dashboard">/g' "$page"
        sed -i 's/class="header-nav-item">/class="header-nav-item" data-i18n="Dashboard">/g' "$page"
        
        echo "✓ $page actualizado"
    fi
done

echo "¡Completado!"
