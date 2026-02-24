# ⚡ Guía Rápida: Instalar OrdenC como App en Teléfono

## 🎯 Pasos Simples (5 minutos)

### Paso 1: Asegúrate que está en HTTPS
Tu app DEBE estar en un dominio HTTPS (no HTTP):
- ✅ Heroku: Ya tiene HTTPS automático
- ✅ PythonAnywhere: Ya tiene HTTPS gratis
- ✅ Otros: Configura SSL/TLS

**Ejemplo de URL correcta:**
```
https://miapp.herokuapp.com      ← CORRECTO
https://mi-dominio.com           ← CORRECTO
http://miapp.herokuapp.com       ← NO FUNCIONA (sin S)
```

### Paso 2: Abre en el Teléfono

**Android (Chrome o Edge):**
1. Abre Chrome en tu teléfono
2. Escribe: `https://tu-app.com` (reemplaza con tu dominio real)
3. Presiona Enter
4. **ESPERA 3-5 segundos**
5. Verás un banner: "Instalar OrdenC" o "Install"
6. Toca "Instalar"

**iPhone/iPad (Safari):**
1. Abre Safari
2. Ve a: `https://tu-app.com`
3. Toca el icono Compartir (↗️) abajo
4. Selecciona "Agregar a pantalla de inicio"
5. Toca "Agregar"

### Paso 3: ¡Listo! 🎉

La app aparecerá en tu pantalla de inicio como una app normal.

---

## 🆘 Si No Ves el Banner "Instalar"

### Verifica:

1. **¿Está en HTTPS?**
   ```bash
   # Abre en la PC el navegador y prueba:
   # https://tu-dominio.com
   ```
   - ✅ Si te muestra la app: OK
   - ❌ Si muestra error de SSL: configura HTTPS

2. **¿Espéraste 3-5 segundos?**
   - El banner tarda en aparecer
   - Recarga la página (F5) si esperas mucho

3. **¿Usas Chrome o navegador compatible?**
   - Android: Chrome, Edge, Brave
   - iPhone: Safari ESENCIAL
   - ❌ Firefox tiene soporte limitado

4. **¿Está el manifest.json disponible?**
   ```bash
   curl https://tu-dominio.com/manifest.json
   # Debe retornar JSON (no error)
   ```

---

## 📱 Qué Funciona como App Instalada

| Característica | Funciona |
|---|---|
| Se abre sin navegador | ✅ Sí |
| Funciona offline (parcial) | ✅ Sí |
| Se actualiza automáticamente | ✅ Sí |
| Aparece en búsqueda | ✅ Sí |
| Se puede compartir | ✅ Sí |
| Notificaciones (futuro) | ⚙️ Configurable |

---

## 🔄 Desinstalar o Actualizar

**Android:**
- Menú largo en el icono → "Desinstalar app"
- Se actualiza automáticamente cuando abres la URL

**iPhone:**
- Menú largo en el icono → "Eliminar app"
- Se actualiza automáticamente

---

## 💡 Consejos

### Para Testing Local (Sin Desplegar)

Si quieres probar en dev antes de desplegar:

```bash
# Opción 1: Usar ngrok (RECOMENDADO)
pip install ngrok
# O descargarlo: https://ngrok.com/download

ngrok http 5000
# Te dará: https://abc123.ngrok.io

# Usa esa URL en el teléfono (válida por 2 horas)
```

```bash
# Opción 2: En red local (solo Android)
# Si tu PC y teléfono están en la misma WiFi:

# Abre en teléfono: http://tu-ip-pc:5000
# No necesita HTTPS en local, pero cacheará parcialmente
```

---

## 🚀 Siguiente Paso: APK Google Play (Opcional)

Si quieres un **APK distribuible** para Play Store:

```bash
npm install -g @bubblewrap/cli
bubblewrap init --manifest https://tu-app.com/manifest.json
# Seguir pasos...

# Resultado: app.aab para Play Store
```

O usa [PWABuilder](https://www.pwabuilder.com) - más visual.

---

## 📞 Troubleshooting Rápido

| Problema | Solución |
|---|---|
| "El sitio no es seguro" | Usa HTTPS. Heroku lo tiene automático |
| No veo el banner | Espera 5 seg. Recarga. Usa Chrome |
| Funciona en web pero no como app | El manifest.json no está accesible. Verifica la URL |
| Dice que no se puede instalar | El dominio no está en HTTPS |
| Se ve feo en teléfono | Es normal en primera instalación. Recarga |

---

## ✅ Checklist Final

```
[ ] Mi dominio es HTTPS (no HTTP)
[ ] Puedo abrir la URL en Chrome del teléfono
[ ] Espéré 3-5 segundos
[ ] Vi el banner "Instalar"
[ ] Toqué instalar
[ ] La app está en mi pantalla de inicio
[ ] Puedo abrirla sin navegador
```

---

**¡Eso es todo! Tu app ya es PWA y funciona como app nativa.** 🎉

Para dudas detalladas: ver `docs/PWA_INSTALACION.md`
