# 🚀 Despliegue con HTTPS para PWA

Como mencionaste que ya tienes desplegado en Anywhere/Heroku, aquí están las instrucciones para asegurar que tu PWA funcione perfectamente como app en teléfono.

## ¿Por Qué HTTPS es Obligatorio?

- Las PWAs **REQUIEREN HTTPS** para:
  - Service Workers (caché offline)
  - Notificaciones push
  - Acceso a dispositivos (cámara, GPS, etc.)
  - Instalación como app

## 🔧 Si Usas Heroku

```bash
# Tu app ya tiene HTTPS automátic en Heroku
# Solo verifica que el dominio sea tu-app.herokuapp.com

# Para verificar que funciona:
curl -I https://tu-app.herokuapp.com

# Debería mostrar HTTP/1.1 200 OK u otro código 2xx/3xx
```

### Configuración Recomendada en Heroku:

1. **Procfile** (debe existir):
```
web: gunicorn backend.app:create_app()
```

2. **requirements.txt** (añade si falta):
```
gunicorn==21.2.0
```

3. **Config vars en Heroku Dashboard**:
```
FLASK_ENV = production
FLASK_DEBUG = 0
```

## 🌐 Si Usas PythonAnywhere

PythonAnywhere ofrece SSL gratis:

1. Dashboard → Tu dominio
2. Security → Force HTTPS
3. Te dan certificado automático

## 🛠️ Para Otros Servicios

| Servicio | SSL | Instrucciones |
|---|---|---|
| **Heroku** | Automático | Dashboard → Settings → Domains |
| **PythonAnywhere** | Gratis | Security → Force HTTPS |
| **Google Cloud** | Auto staging | Cloud Load Balancer |
| **AWS** | ACM (gratis) | Certificate Manager |
| **Render** | Automático | Auto-deployed |

## ✅ Checklist Antes de Instalar como App

### 1. Verifica HTTPS:
```bash
# En tu máquina o en el teléfono
curl -I https://tu-app.env.com
# Debe responder 200/301/302, no 0 (timeout)
```

### 2. Verifica el Manifest:
```bash
curl https://tu-app.env.com/manifest.json

# Debe retornar JSON válido con:
# - "name": "OrdenC - Financial Manager"
# - "start_url": "/html/login.html"
# - "display": "standalone"
```

### 3. Verifica el Service Worker:
```bash
curl https://tu-app.env.com/service-worker.js

# Debe retornar JavaScript válido
```

### 4. Verifica la URL en el Navegador del Teléfono:
- Abre `https://tu-app.env.com` en Chrome/Edge
- Espera 3-5 segundos
- Debe aparecer el prompt "Instalar OrdenC" en la parte superior

## 📱 Instalación Final

### Android:

1. **Opción A: Automática**
   - Abre la app en Chrome
   - Espera el banner
   - Toca "Instalar"

2. **Opción B: Manual**
   - Menú (⋮) → "Instalar aplicación"
   - O Menú (⋮) → "Agregar a pantalla de inicio"

### iPhone/iPad:

1. Abre en Safari
2. Compartir (↗️) → "Agregar a pantalla de inicio"
3. Dale un nombre
4. Toca "Agregar"

## 🐛 Troubleshooting SSL

### Problema: "El sitio no es seguro"

```bash
# Verifica el certificado
openssl s_client -connect tu-app.env.com:443

# Si el certificado es válido, verifica DNS:
nslookup tu-app.env.com

# Si los DNS están OK, espera 15 minutos (SSL tarda en propagarse)
```

### Problema: Certificado auto-firmado

- Algunos servicios como servidor local usan certs auto-firmados
- No funcionan para PWA en teléfono
- Usa **ngrok** para desarrollo:

```bash
# Instala ngrok desde https://ngrok.com
# Luego:

ngrok http 5000

# Te dará una URL como https://abc123.ngrok.io
# Usa esa URL en el teléfono (incluye https://)
```

## 🎯 Testing Local con HTTPS

### Opción 1: ngrok (Más fácil)

```bash
# Terminal 1: Ejecuta tu app Flask normalmente
python backend/app.py

# Terminal 2: Expone con ngrok
ngrok http 5000

# Abrirá:
# https://abc123.ngrok.io ← USA ESTA URL en teléfono
```

### Opción 2: Crear certificado local

```bash
# Crear certificado autofirmado
openssl req -x509 -newkey rsa:4096 -nodes -out cert.pem -keyout key.pem -days 365

# Ejecutar Flask con SSL
python -c "
from backend.app import create_app
app = create_app()
app.run(ssl_context=('cert.pem', 'key.pem'), host='0.0.0.0', port=5000)
"

# En teléfono: acepta la advertencia (cert autofirmado)
# URL: https://tu-ip:5000
```

## 📊 Checklist Final

- [ ] App desplegada en servidor con HTTPS
- [ ] URL es `https://` (no `http://`)
- [ ] Certificado SSL válido (nno auto-firmado)
- [ ] `/manifest.json` accesible
- [ ] `/service-worker.js` accesible
- [ ] `/html/login.html` accesible
- [ ] Puedes abrir URL en teléfono Chrome
- [ ] Ves el prompt "Instalar OrdenC"
- [ ] Google Play Console (opcional, para APK)

## 🔗 URLs Útiles

- [Google PWA Testing](https://developers.google.com/web/tools/chrome-devtools/progressive-web-apps)
- [PWA Validator](https://www.pwabuilder.com)
- [Heroku SSL Setup](https://devcenter.heroku.com/articles/automated-certificate-management)
- [ngrok Documentación](https://ngrok.com/docs)

---

**Resumen rápido:**
1. ✅ Tu app ya es PWA
2. ✅ Verifica HTTPS en tu despliegue
3. ✅ Abre en Chrome del teléfono
4. ✅ Instala cuando veas el prompt
5. ✅ ¡Disfruta como app nativa! 🎉
