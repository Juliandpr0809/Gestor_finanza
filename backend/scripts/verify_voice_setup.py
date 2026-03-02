#!/usr/bin/env python
"""
Script para verificar que los servicios de voz están configurados correctamente
"""

print("🔍 Verificando configuración de servicios de voz...\n")

# 1. Verificar instalaciones
print("=" * 50)
print("1️⃣ Verificando dependencias instaladas")
print("=" * 50)

try:
    from deepgram import DeepgramClient
    print("✅ deepgram-sdk: Instalado")
except ImportError as e:
    print(f"❌ deepgram-sdk: No instalado - {e}")

try:
    from gtts import gTTS
    print("✅ gTTS: Instalado")
except ImportError as e:
    print(f"❌ gTTS: No instalado - {e}")

try:
    import pyttsx3
    print("✅ pyttsx3: Instalado")
except ImportError as e:
    print(f"❌ pyttsx3: No instalado - {e}")

# 2. Verificar variable de entorno
print("\n" + "=" * 50)
print("2️⃣ Verificando configuración")
print("=" * 50)

import os
from dotenv import load_dotenv

load_dotenv()

deepgram_key = os.environ.get('DEEPGRAM_API_KEY')
if deepgram_key:
    print(f"✅ DEEPGRAM_API_KEY: Configurada ({deepgram_key[:10]}...)")
else:
    print("❌ DEEPGRAM_API_KEY: No encontrada en .env")

# 3. Verificar servicios
print("\n" + "=" * 50)
print("3️⃣ Verificando servicios")
print("=" * 50)

try:
    from services.voice_service import voice_service
    if voice_service.enabled:
        print("✅ VoiceService (Deepgram): Inicializado correctamente")
    else:
        print("⚠️  VoiceService: Cargado pero no habilitado (falta API key)")
except Exception as e:
    print(f"❌ VoiceService: Error al cargar - {e}")

try:
    from services.tts_service import tts_service
    print("✅ TTSService (gTTS + pyttsx3): Inicializado correctamente")
except Exception as e:
    print(f"❌ TTSService: Error al cargar - {e}")

# 4. Resumen final
print("\n" + "=" * 50)
print("📊 RESUMEN")
print("=" * 50)

all_ok = True

if not deepgram_key:
    print("⚠️  Falta configurar DEEPGRAM_API_KEY en .env")
    all_ok = False

try:
    from services.voice_service import voice_service
    from services.tts_service import tts_service
    
    if not voice_service.enabled:
        print("⚠️  Deepgram no está habilitado")
        all_ok = False
        
except:
    print("❌ Error al importar servicios")
    all_ok = False

if all_ok:
    print("\n🎉 ¡Todo configurado correctamente!")
    print("\n📝 Próximos pasos:")
    print("   1. Iniciar el backend: python backend/app.py")
    print("   2. Abrir en navegador: http://localhost:5000/voice-chat.html")
    print("   3. Hacer login en la app primero")
    print("   4. ¡Probar el chat de voz!")
else:
    print("\n⚠️  Hay algunos problemas de configuración")
    print("\n📝 Para corregir:")
    print("   1. Verificar que DEEPGRAM_API_KEY esté en backend/.env")
    print("   2. Reiniciar el backend después de agregar la key")

print("\n" + "=" * 50)
