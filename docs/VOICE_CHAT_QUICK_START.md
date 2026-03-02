# 🚀 Guía Rápida: Implementación de Chat de Voz

## ⚡ Inicio Rápido (30 minutos)

Esta guía te llevará desde cero hasta tener un sistema de voz a voz funcionando en 30 minutos.

### Prerrequisitos

```bash
# Python 3.8+
python --version

# Pip actualizado
pip install --upgrade pip

# Git (para clonar si es necesario)
git --version
```

---

## 📦 Paso 1: Instalación de Dependencias (10 min)

### Backend

```bash
# Navegar al backend
cd backend

# Instalar dependencias de voz
pip install openai-whisper==20231117
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
pip install gTTS==2.5.0
pip install pyttsx3==2.90
pip install pydub==0.25.1
pip install flask-socketio==5.3.6
pip install python-socketio[client]==5.11.1

# Verificar instalación
python -c "import whisper; print('Whisper OK')"
python -c "from gtts import gTTS; print('gTTS OK')"
python -c "import pyttsx3; print('pyttsx3 OK')"
```

### Descargar Modelo Whisper

```bash
# Descargar modelo 'small' (más rápido para empezar)
python -c "import whisper; model = whisper.load_model('small'); print('Modelo descargado')"

# Alternativa: 'medium' (mejor precisión, más lento)
# python -c "import whisper; model = whisper.load_model('medium')"
```

---

## 🏗️ Paso 2: Crear Servicios de Voz (10 min)

### Crear `backend/services/voice_service.py`

```bash
touch backend/services/voice_service.py
```

**Contenido:**

```python
"""
Servicio de Speech-to-Text usando OpenAI Whisper
"""
import whisper
import torch
import os

class VoiceService:
    def __init__(self):
        # Cargar modelo Whisper
        model_name = os.environ.get('WHISPER_MODEL', 'small')  # small/medium/large
        self.model = whisper.load_model(model_name)
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"[VOICE SERVICE] Whisper model '{model_name}' loaded on {self.device}")
    
    def transcribe(self, audio_file_path, language='es'):
        """
        Transcribe audio a texto
        
        Args:
            audio_file_path: Ruta al archivo de audio
            language: Código de idioma (es, en, etc.)
        
        Returns:
            str: Texto transcrito
        """
        try:
            result = self.model.transcribe(
                audio_file_path,
                language=language,
                task="transcribe",
                fp16=False  # CPU safe
            )
            
            transcribed_text = result["text"].strip()
            print(f"[VOICE SERVICE] Transcribed: {transcribed_text}")
            
            return transcribed_text
            
        except Exception as e:
            print(f"[VOICE SERVICE ERROR] Transcription failed: {e}")
            raise

# Singleton instance
voice_service = VoiceService()
```

---

### Crear `backend/services/tts_service.py`

```bash
touch backend/services/tts_service.py
```

**Contenido:**

```python
"""
Servicio de Text-to-Speech con gTTS (primario) y pyttsx3 (fallback)
"""
from gtts import gTTS
import pyttsx3
import hashlib
import os
from pathlib import Path

class TTSService:
    def __init__(self):
        # Directorio de caché
        self.cache_dir = Path("instance/audio_cache")
        self.cache_dir.mkdir(exist_ok=True, parents=True)
        
        # Configurar motor offline (fallback)
        self.offline_engine = pyttsx3.init()
        self.offline_engine.setProperty('rate', 150)  # Velocidad
        self.offline_engine.setProperty('volume', 0.9)
        
        print("[TTS SERVICE] Initialized with gTTS (primary) + pyttsx3 (fallback)")
    
    def synthesize(self, text, language='es', use_cache=True):
        """
        Genera audio a partir de texto
        
        Args:
            text: Texto a sintetizar
            language: Código de idioma (es, en, etc.)
            use_cache: Usar caché si está disponible
        
        Returns:
            Path: Ruta al archivo de audio generado
        """
        # Verificar caché
        if use_cache:
            cached_file = self._get_cached_audio(text)
            if cached_file:
                print(f"[TTS SERVICE] Using cached audio")
                return cached_file
        
        # Intentar gTTS primero
        try:
            audio_path = self._synthesize_gtts(text, language)
            print(f"[TTS SERVICE] Audio generated with gTTS")
            return audio_path
        except Exception as e:
            print(f"[TTS SERVICE] gTTS failed: {e}. Using offline fallback...")
            return self._synthesize_offline(text)
    
    def _synthesize_gtts(self, text, language):
        """Síntesis con Google TTS (online)"""
        file_path = self.cache_dir / f"{self._text_hash(text)}.mp3"
        
        tts = gTTS(text=text, lang=language, slow=False)
        tts.save(str(file_path))
        
        return file_path
    
    def _synthesize_offline(self, text):
        """Síntesis offline con pyttsx3"""
        file_path = self.cache_dir / f"{self._text_hash(text)}_offline.mp3"
        
        self.offline_engine.save_to_file(text, str(file_path))
        self.offline_engine.runAndWait()
        
        return file_path
    
    def _get_cached_audio(self, text):
        """Busca audio en caché"""
        # Buscar versión online
        file_path = self.cache_dir / f"{self._text_hash(text)}.mp3"
        if file_path.exists():
            return file_path
        
        # Buscar versión offline
        file_path_offline = self.cache_dir / f"{self._text_hash(text)}_offline.mp3"
        if file_path_offline.exists():
            return file_path_offline
        
        return None
    
    def _text_hash(self, text):
        """Genera hash único para texto"""
        return hashlib.md5(text.encode('utf-8')).hexdigest()
    
    def clear_cache(self, max_age_days=7):
        """Limpia caché antiguo"""
        import time
        cutoff = time.time() - (max_age_days * 86400)
        
        deleted = 0
        for file in self.cache_dir.glob("*.mp3"):
            if file.stat().st_mtime < cutoff:
                file.unlink()
                deleted += 1
        
        print(f"[TTS SERVICE] Cleared {deleted} cached files")

# Singleton instance
tts_service = TTSService()
```

---

## 🔌 Paso 3: Crear Endpoint de Prueba (5 min)

### Agregar a `backend/routes/chat.py`

```python
# Al inicio del archivo, agregar imports
from services.voice_service import voice_service
from services.tts_service import tts_service
import base64
from pathlib import Path
import uuid

# Agregar al final del archivo
@chat_bp.route('/voice/test', methods=['POST'])
def voice_test():
    """
    Endpoint de prueba para voz a voz
    Recibe: audio en base64
    Retorna: transcripción + audio de respuesta
    """
    user, error = get_user()
    if error:
        return error
    
    try:
        # 1. Recibir audio
        data = request.get_json()
        audio_base64 = data.get('audio')
        
        if not audio_base64:
            return jsonify({'error': 'No audio provided'}), 400
        
        # 2. Guardar audio temporalmente
        audio_data = base64.b64decode(audio_base64)
        temp_audio_dir = Path("instance/temp_audio")
        temp_audio_dir.mkdir(exist_ok=True, parents=True)
        temp_file = temp_audio_dir / f"voice_{uuid.uuid4()}.wav"
        temp_file.write_bytes(audio_data)
        
        # 3. Speech-to-Text (Whisper)
        transcription = voice_service.transcribe(str(temp_file))
        
        # 4. Procesar con IA (Groq)
        response = ai_service.chat(user.id, transcription)
        
        # 5. Text-to-Speech
        audio_response_path = tts_service.synthesize(response)
        
        # 6. Leer audio generado
        with open(audio_response_path, 'rb') as f:
            audio_response_data = base64.b64encode(f.read()).decode('utf-8')
        
        # 7. Limpiar archivo temporal
        temp_file.unlink()
        
        return jsonify({
            'transcription': transcription,
            'response_text': response,
            'response_audio': audio_response_data,
            'audio_format': 'mp3'
        }), 200
        
    except Exception as e:
        print(f"Error in voice test: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'error': 'Voice processing failed',
            'details': str(e)
        }), 500
```

---

## 🎨 Paso 4: Crear Frontend de Prueba (5 min)

### Crear `frontend/html/voice-test.html`

```html
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Prueba de Voz - OrdenC</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 600px;
            margin: 50px auto;
            padding: 20px;
            text-align: center;
        }
        
        #voiceButton {
            width: 150px;
            height: 150px;
            border-radius: 50%;
            border: none;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            font-size: 48px;
            cursor: pointer;
            transition: transform 0.2s;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        }
        
        #voiceButton:hover {
            transform: scale(1.05);
        }
        
        #voiceButton.recording {
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            animation: pulse 1.5s infinite;
        }
        
        @keyframes pulse {
            0%, 100% { transform: scale(1); }
            50% { transform: scale(1.1); }
        }
        
        #status {
            margin-top: 20px;
            font-size: 18px;
            color: #666;
        }
        
        #transcription, #response {
            margin-top: 20px;
            padding: 15px;
            background: #f5f5f5;
            border-radius: 8px;
            display: none;
        }
        
        .label {
            font-weight: bold;
            color: #667eea;
            margin-bottom: 5px;
        }
    </style>
</head>
<body>
    <h1>🎙️ Prueba de Chat de Voz</h1>
    
    <button id="voiceButton">🎤</button>
    
    <div id="status">Presiona el botón para hablar</div>
    
    <div id="transcription">
        <div class="label">📝 Transcripción:</div>
        <div id="transcriptionText"></div>
    </div>
    
    <div id="response">
        <div class="label">💬 Respuesta:</div>
        <div id="responseText"></div>
    </div>
    
    <script>
        // Elementos
        const voiceButton = document.getElementById('voiceButton');
        const status = document.getElementById('status');
        const transcriptionDiv = document.getElementById('transcription');
        const transcriptionText = document.getElementById('transcriptionText');
        const responseDiv = document.getElementById('response');
        const responseText = document.getElementById('responseText');
        
        // Estado
        let isRecording = false;
        let mediaRecorder = null;
        let audioChunks = [];
        
        // Botón de voz
        voiceButton.addEventListener('click', () => {
            if (isRecording) {
                stopRecording();
            } else {
                startRecording();
            }
        });
        
        // Iniciar grabación
        async function startRecording() {
            try {
                const stream = await navigator.mediaDevices.getUserMedia({ 
                    audio: {
                        echoCancellation: true,
                        noiseSuppression: true,
                        autoGainControl: true
                    }
                });
                
                mediaRecorder = new MediaRecorder(stream);
                audioChunks = [];
                
                mediaRecorder.ondataavailable = (event) => {
                    audioChunks.push(event.data);
                };
                
                mediaRecorder.onstop = () => {
                    processAudio();
                };
                
                mediaRecorder.start();
                isRecording = true;
                voiceButton.classList.add('recording');
                voiceButton.textContent = '⏹️';
                status.textContent = '🎙️ Grabando... Presiona para detener';
                
                // Ocultar resultados anteriores
                transcriptionDiv.style.display = 'none';
                responseDiv.style.display = 'none';
                
            } catch (error) {
                console.error('Error accessing microphone:', error);
                alert('No se pudo acceder al micrófono. Por favor, permite el acceso.');
            }
        }
        
        // Detener grabación
        function stopRecording() {
            mediaRecorder.stop();
            mediaRecorder.stream.getTracks().forEach(track => track.stop());
            isRecording = false;
            voiceButton.classList.remove('recording');
            voiceButton.textContent = '🎤';
            status.textContent = '⏳ Procesando...';
        }
        
        // Procesar audio
        async function processAudio() {
            const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
            
            // Convertir a base64
            const reader = new FileReader();
            reader.readAsDataURL(audioBlob);
            reader.onloadend = async () => {
                const base64Audio = reader.result.split(',')[1];
                
                // Enviar al backend
                try {
                    const token = localStorage.getItem('token');
                    
                    const response = await fetch('/api/chat/voice/test', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'Authorization': `Bearer ${token}`
                        },
                        body: JSON.stringify({
                            audio: base64Audio
                        })
                    });
                    
                    if (!response.ok) {
                        throw new Error('Error procesando audio');
                    }
                    
                    const result = await response.json();
                    
                    // Mostrar transcripción
                    transcriptionText.textContent = result.transcription;
                    transcriptionDiv.style.display = 'block';
                    
                    // Mostrar respuesta
                    responseText.textContent = result.response_text;
                    responseDiv.style.display = 'block';
                    
                    // Reproducir audio de respuesta
                    const audioResponse = document.createElement('audio');
                    audioResponse.src = `data:audio/mp3;base64,${result.response_audio}`;
                    audioResponse.play();
                    
                    status.textContent = '✅ Listo - Presiona para hablar de nuevo';
                    
                } catch (error) {
                    console.error('Error processing voice:', error);
                    status.textContent = '❌ Error procesando voz';
                    alert('Error: ' + error.message);
                }
            };
        }
    </script>
</body>
</html>
```

---

## 🧪 Paso 5: Probar el Sistema

### 1. Iniciar Backend

```bash
cd backend
python app.py
```

### 2. Abrir Frontend

Navegar a:
```
http://localhost:5000/voice-test.html
```

### 3. Realizar Prueba

1. **Hacer login** primero en la aplicación principal para obtener token
2. Presionar botón de micrófono 🎤
3. **Decir**: "Hola, ¿cuál es mi balance?"
4. Presionar de nuevo para detener ⏹️
5. **Esperar**: Procesamiento (~2-4 segundos)
6. **Escuchar**: Respuesta en voz del sistema

### 4. Comandos de Prueba

Prueba estos comandos para verificar funcionalidad:

```
✅ "Hola, ¿cuál es mi balance?"
✅ "Gasté cincuenta dólares en supermercado"
✅ "¿Cuánto gasté este mes?"
✅ "Registra un ingreso de mil dólares"
✅ "Dame consejos para ahorrar"
```

---

## 🔧 Troubleshooting

### Problema: "Whisper model failed to load"

**Solución:**
```bash
# Re-descargar modelo
rm -rf ~/.cache/whisper
python -c "import whisper; whisper.load_model('small')"
```

### Problema: "Microphone access denied"

**Solución:**
- Chrome: Configuración → Privacidad → Configuración de sitios → Micrófono → Permitir
- Edge: Similar a Chrome
- Firefox: Permisos → Micrófono → Permitir para localhost

### Problema: "gTTS failed"

**Solución:**
```bash
# Verificar conexión a internet
ping google.com

# Si no hay internet, el sistema usará pyttsx3 automáticamente
# Para forzar offline:
# Editar tts_service.py → return self._synthesize_offline(text)
```

### Problema: "Audio muy lento"

**Solución:**
```bash
# Cambiar a modelo 'tiny' (más rápido, menos preciso)
# En voice_service.py:
# self.model = whisper.load_model('tiny')

# O usar GPU si está disponible
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

---

## 📊 Verificar Instalación

Script de verificación (`backend/scripts/verify_voice_setup.py`):

```python
#!/usr/bin/env python
"""
Verifica que todos los componentes de voz estén instalados correctamente
"""

def verify_installations():
    print("🔍 Verificando instalación de componentes de voz...\n")
    
    # 1. Whisper
    try:
        import whisper
        model = whisper.load_model("small")
        print("✅ Whisper: OK (modelo 'small' cargado)")
    except Exception as e:
        print(f"❌ Whisper: FAIL - {e}")
    
    # 2. gTTS
    try:
        from gtts import gTTS
        tts = gTTS("Prueba", lang='es')
        print("✅ gTTS: OK")
    except Exception as e:
        print(f"❌ gTTS: FAIL - {e}")
    
    # 3. pyttsx3
    try:
        import pyttsx3
        engine = pyttsx3.init()
        print("✅ pyttsx3: OK")
    except Exception as e:
        print(f"❌ pyttsx3: FAIL - {e}")
    
    # 4. PyDub
    try:
        from pydub import AudioSegment
        print("✅ pydub: OK")
    except Exception as e:
        print(f"❌ pydub: FAIL - {e}")
    
    # 5. Flask-SocketIO
    try:
        from flask_socketio import SocketIO
        print("✅ Flask-SocketIO: OK")
    except Exception as e:
        print(f"❌ Flask-SocketIO: FAIL - {e}")
    
    print("\n✨ Verificación completa!")

if __name__ == '__main__':
    verify_installations()
```

Ejecutar:
```bash
python backend/scripts/verify_voice_setup.py
```

---

## 🎯 Próximos Pasos

Una vez que la prueba básica funcione:

1. **Implementar WebSocket** (mejor UX, menor latencia)
   - Ver `docs/VOICE_CHAT_REDESIGN_SPEC.md` - Fase 4

2. **Agregar más intenciones** (crear cuentas, transferencias, etc.)
   - Ver `docs/VOICE_CHAT_REDESIGN_SPEC.md` - Sección "Mapeo de Comandos"

3. **Optimizar latencia** (caché, GPU, modelo más pequeño)
   - Ver `docs/VOICE_CHAT_REDESIGN_SPEC.md` - Sección "Performance"

4. **Mejorar UI** (animaciones, feedback visual)
   - Ver `docs/VOICE_CHAT_REDESIGN_SPEC.md` - Fase 5

---

## 📚 Recursos Adicionales

- **Especificación Completa**: `docs/VOICE_CHAT_REDESIGN_SPEC.md`
- **Documentación Whisper**: https://github.com/openai/whisper
- **Documentación gTTS**: https://gtts.readthedocs.io/
- **Ejemplos de Comandos**: Ver archivo de especificación completa

---

## 🆘 Ayuda

Si encuentras problemas:

1. Revisa la sección **Troubleshooting** arriba
2. Consulta `docs/VOICE_CHAT_REDESIGN_SPEC.md` para detalles técnicos
3. Verifica logs del backend: `tail -f backend/logs/app.log`
4. Abre el navegador con consola de desarrollo (F12)

---

**¡Feliz desarrollo!** 🎙️💰
