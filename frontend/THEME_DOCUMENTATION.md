# 🎨 Cracker - Sistema de Diseño Visual

## Descripción

Cracker utiliza un **sistema de diseño moderno y cohesivo** inspirado en aplicaciones fintech premium como N26, Revolut y Stripe. El diseño enfatiza:

- **Minimalismo elegante** con gradientes sutiles
- **Accesibilidad de alto contraste** (tema oscuro profesional)
- **Componentes consistentes** en todas las vistas
- **Experiencia de usuario fluida** con transiciones suaves
- **Responsividad total** (móvil, tablet, escritorio)

## Estructura de Temas

### Archivos CSS Principales

1. **`modern-theme.css`** (1900+ líneas)
   - Variables CSS globales (colores, sombras, espaciado)
   - Componentes base: header, buttons, forms, tables
   - Grid system y utilities
   - Temas específicos (badges, modales, dropdowns)

2. **`unified-pages.css`** (500+ líneas)
   - Estilos unificados para todas las páginas
   - Componentes de página: headers, cards, transacciones
   - Tablas, formularios y estados vacíos
   - Breakpoints responsive

3. **Archivos Específicos de Vista** (conservados para customización)
   - `auth.css` - Páginas de login/registro
   - `accounts.css` - Vista de cuentas
   - `transactions.css` - Historial de transacciones
   - `ai-chat.css` - Chat IA
   - Etc.

## Paleta de Colores

### Variables de Tema
```css
/* Primario */
--primary-gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%)
--secondary-gradient: linear-gradient(135deg, #f093fb 0%, #f5576c 100%)
--accent-gradient: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)

/* Fondos */
--bg-dark: #0f0f1e
--bg-darker: #0a0a14
--bg-card: #1a1a2e
--bg-card-hover: #252541

/* Texto */
--text-primary: #ffffff
--text-secondary: #b0b0c0
--text-tertiary: #8a8a9e

/* Estados */
--success: #10b981 (verde)
--warning: #f59e0b (amarillo)
--danger: #ef4444 (rojo)
--info: #3b82f6 (azul)
```

## Componentes Principales

### Header
- Logo con gradiente
- Navegación superior
- Acciones rápidas (chat, micrófono, notificaciones)
- Menu de usuario con dropdown

### Cards
- Efecto hover con elevación
- Bordes suaves (border-radius: 16px)
- Transiciones fluidas
- Estados interactivos

### Botones
- **Primario**: Gradiente purpura-azul
- **Secundario**: Fondo oscuro con borde
- **Success/Danger**: Colores de estado
- **Small**: Versión compacta

### Formularios
- Inputs con tema oscuro
- Focus con brillo gradiente
- Placeholders sutiles
- Estados deshabilitados

### Tablas
- Headers con fondo oscuro
- Filas con hover interactivo
- Alineación clara
- Bordes verticales

## Uso en Páginas

### En HTML
```html
<!-- Base obligatoria -->
<link rel="stylesheet" href="../css/modern-theme.css">
<link rel="stylesheet" href="../css/unified-pages.css">

<!-- Personalización específica (opcional) -->
<link rel="stylesheet" href="../css/accounts.css">
```

### Ejemplo de Estructura
```html
<div class="container">
  <div class="page-header">
    <div class="page-header-left">
      <h1>Mis Cuentas</h1>
      <p>Gestiona todas tus cuentas financieras</p>
    </div>
    <div class="page-header-right">
      <button class="btn btn-primary">+ Nueva Cuenta</button>
    </div>
  </div>

  <div class="accounts-grid">
    <!-- Account cards -->
  </div>
</div>
```

## Clases Utilitarias

### Espaciado
- `mt-1` a `mt-4` - Margin top
- `mb-1` a `mb-4` - Margin bottom
- `p-2` a `p-4` - Padding

### Tipografía
- `text-center` - Centrado
- `text-right` - Alineado derecha

### Visibilidad
- `opacity-50` - 50% de opacidad
- `opacity-75` - 75% de opacidad

### Interacción
- `cursor-pointer` - Puntero interactivo

## Estados y Transiciones

### Hover
- Cards: `translateY(-2px)` + sombra
- Botones: `translateY(-2px)` + sombra
- Items: cambio de background

### Focus
- Input/Select: brillo azul
- Enlaces: cambio de color

### Animaciones
- Duración: 300ms (estándar)
- Timing: ease (suave)
- Loading spinner: rotación infinita

## Responsive Design

### Breakpoints
- **Desktop**: 1400px máximo
- **Tablet**: max-width 1024px
- **Mobile**: max-width 640px

### Cambios por Tamaño
- Tablet: Una columna en grillas, padding reducido
- Mobile: Fullwidth, header apilado, tablas comprimidas

## Colores por Contexto

### Transacciones
- **Ingreso**: Verde (#10b981)
- **Gasto**: Rojo/blanco (dependiendo contexto)

### Estados
- **Éxito**: Verde
- **Advertencia**: Amarillo
- **Error**: Rojo
- **Info**: Azul

## Personalización

### Para cambiar colores globales
Modifica variables en `modern-theme.css`:
```css
:root {
  --primary-gradient: linear-gradient(...);
  --bg-dark: #...;
}
```

### Para agregar nuevas clases
Agregalas en `unified-pages.css` siguiendo el patrón BEM:
```css
.component-name {
  ...
}

.component-name:hover {
  ...
}
```

## Consideraciones de Accesibilidad

✅ Contraste WCAG AA (4.5:1 o superior)
✅ Focus visible en interactivos
✅ Colores + iconos (no solo color)
✅ Textos descriptivos en botones
✅ Espaciado suficiente para toques

## Navegadores Soportados

- Chrome/Edge 90+
- Firefox 88+
- Safari 14+
- Mobile Safari iOS 14+

## Fuentes

Sistema de fuentes del SO (system font stack):
```
-apple-system, BlinkMacSystemFont, 'SF Pro Display', 'Inter', 'Segoe UI', sans-serif
```

## Performance

- CSS modular y escalable
- Sin animaciones pesadas
- Media queries eficientes
- Variables CSS reutilizables

## Cambios Recientes

### ✨ Versión 2.0 (Actual)
- Nuevo `modern-theme.css` con paleta unificada
- Sistema de grid mejorado
- Header interactivo con dropdown
- Badges y componentes de estado
- Máxima consistencia entre vistas

### 🔄 Migración desde minimalist-clean.css
Todas las páginas ahora usan:
1. `modern-theme.css` - Base global
2. `unified-pages.css` - Componentes de página
3. Hojas específicas (si necesitan customización)

## Soporte

Para problemas con estilos:
1. Verificar que los 2 archivos CSS base se carguen
2. Revisar orden de importación (modern-theme primero)
3. Buscar conflictos en hojas específicas
4. Probar en navegador incógnito (sin cache)
