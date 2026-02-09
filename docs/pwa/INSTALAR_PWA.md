# 📱 Instalación de OrdenC como App Nativa en Android/iOS

## ¿Qué es PWA?
**Progressive Web App (PWA)** es una aplicación web que funciona como una app nativa instalada en tu teléfono, sin necesidad de descargarla desde Play Store o App Store.

## ✅ Características de OrdenC como PWA

- ✨ **Instalable nativamente** en Android e iOS
- 📴 **Funciona sin internet** (datos cacheados)
- 🚀 **Carga rápida** como una app nativa
- 💾 **Sincronización automática** cuando vuelve la conexión
- 🎨 **Diseño nativo** optimizado para móvil
- 🔔 **Notificaciones push** (próximamente)

## 🔧 Cómo Instalar en Android

### Opción 1: Desde Chrome/Firefox (Recomendado)

1. **Abre la URL en Chrome o Firefox:**
   ```
   https://7s6jg2wd-5000.use.devtunnels.ms/html/index.html
   ```

2. **Espera el prompt de instalación:**
   - En Chrome: Veras "Instalar OrdenC" en la parte superior
   - En Firefox: Toca el menú (⋮) → "Instalar" o "Agregar a pantalla de inicio"

3. **Toca "Instalar"** y confirma

4. **¡Listo!** La app aparecerá en tu pantalla de inicio como una app nativa

### Opción 2: Agregar a Pantalla de Inicio (Compatible con más navegadores)

1. Abre la URL en tu navegador
2. Toca el menú (⋮) o ⋯
3. Selecciona "Agregar a pantalla de inicio" o "Add to Home Screen"
4. Confirma el nombre y ícono
5. ¡Listo!

## 🍎 Cómo Instalar en iOS

1. **Abre en Safari** (la PWA funciona mejor en Safari en iOS):
   ```
   https://7s6jg2wd-5000.use.devtunnels.ms/html/index.html
   ```

2. **Toca el botón compartir** (↗️)

3. **Busca "Agregar a pantalla de inicio"**

4. **Personalize si lo deseas** (nombre, ícono)

5. **Toca "Agregar"**

6. ¡La app aparecerá en tu pantalla de inicio!

## 🎯 Diferencias: App vs Navegador

| Feature | PWA OrdenC | Navegador |
|---------|-------------|-----------|
| Ícono en pantalla de inicio | ✅ Sí | ❌ No |
| Barra de dirección | ❌ Oculta | ✅ Visible |
| Carga rápida | ✅ Muy rápida | ⚠️ Más lenta |
| Offline | ✅ Parcial | ❌ No |
| Notificaciones | ✅ Sí (próximamente) | ⚠️ Limitadas |
| Se siente como app nativa | ✅ Sí | ❌ No |

## 💡 Consejos

### Para mejor experiencia en móvil:
- **Modo oscuro**: La app se adapta automáticamente
- **Botones grandes**: Optimizados para tocar con dedos
- **Scroll suave**: Transiciones nativas de iOS/Android
- **Safe Area**: Se adapta a notches y barras de estado

### Mantenimiento de caché:
- Los datos se cachean automáticamente
- Borrar caché del navegador: Ajustes → Apps → [Tu navegador] → Almacenamiento → Borrar caché
- La app se sincroniza automáticamente cuando hay conexión

## 🔄 Actualizar la App

Cuando actualicemos OrdenC:
1. **Cierra completamente la app**
2. **Vuelve a abrirla**
3. **Se actualizará automáticamente** desde el caché

Para forzar actualización:
- Android: Desliza hacia arriba en la app y tira hacia abajo
- iOS: Toca el botón compartir (↗️) → "Recargar"

## 🐛 Solucionar Problemas

### "No me sale la opción de instalar"
- Asegúrate de estar en HTTPS (✓ Los devtunnels son HTTPS)
- Carga el sitio completamente (espera a que cargue todo)
- Prueba en Chrome (mejor soporte PWA)

### "La app se abre en navegador"
- En el menú (⋮), busca "Abrir en app"
- O desinstala y reinstala siguiendo los pasos arriba

### "No funciona sin internet"
- La app cachea datos, pero la conexión API necesita internet
- Los datos cacheados se mostrarán offline
- Cuando vuelva la conexión, se sincronizará automáticamente

## 📊 Monitoreo

Puedes ver el estado del Service Worker en:
1. Abre DevTools (F12 o menú ⋮ → Más herramientas → Herramientas para desarrolladores)
2. Ve a la pestaña "Application"
3. En el lado izquierdo, busca "Service Workers"
4. Deberías ver "service-worker.js" en estado "activated and running"

## 🎉 ¡Listo!

¡Ya tienes OrdenC funcionando como una app nativa en tu teléfono! 
Disfruta de una experiencia de usuario fluida y rápida.

**Feedback:** Si tienes sugerencias o problemas, contáctanos.
