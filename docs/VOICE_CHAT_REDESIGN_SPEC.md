# 🎙️ Especificación Técnica: Rediseño del Módulo de Chat de Voz

## 📋 Tabla de Contenidos

1. [Resumen Ejecutivo](#resumen-ejecutivo)
2. [Análisis del Estado Actual](#análisis-del-estado-actual)
3. [Objetivos y Requisitos](#objetivos-y-requisitos)
4. [Modelos de IA Recomendados](#modelos-de-ia-recomendados)
5. [Arquitectura Propuesta](#arquitectura-propuesta)
6. [Mapeo de Funciones Financieras a Comandos de Voz](#mapeo-de-funciones-financieras-a-comandos-de-voz)
7. [Stack Tecnológico](#stack-tecnológico)
8. [Consideraciones de Implementación](#consideraciones-de-implementación)
9. [Plan de Implementación por Fases](#plan-de-implementación-por-fases)
10. [Estimación de Costos](#estimación-de-costos)
11. [Riesgos y Mitigación](#riesgos-y-mitigación)
12. [Métricas de Éxito](#métricas-de-éxito)

---

## 🎯 Resumen Ejecutivo

### Objetivo
Transformar el módulo de chat de voz actual en un sistema completo de **interacción voz a voz** que permita a los usuarios gestionar todas las funciones financieras de la aplicación mediante comandos de voz naturales, manteniendo costos operativos mínimos o gratuitos.

### Alcance
- **Reconocimiento de voz** (Speech-to-Text): Captura de comandos de usuario
- **Procesamiento de lenguaje natural** (NLU): Interpretación inteligente de intenciones
- **Ejecución de comandos financieros**: Registro, consulta, eliminación y gestión
- **Síntesis de voz** (Text-to-Speech): Respuestas audibles al usuario
- **Conversación fluida**: Experiencia natural, no basada en comandos rígidos

### Restricciones Críticas
✅ **Costo operativo mínimo** (preferencia por soluciones gratuitas)  
✅ **Compatibilidad con funcionalidades existentes**  
✅ **Experiencia conversacional natural**  
✅ **Latencia baja** (< 2 segundos por interacción)

---

## 📊 Análisis del Estado Actual

### Sistema Actual

#### **Backend**
- **Modelo de IA**: Groq API con `llama-3.3-70b-versatile`
- **Funcionalidad**: Solo procesamiento de texto (chat escrito)
- **Capacidades**:
  - ✅ Comprensión de lenguaje natural en español
  - ✅ Gestión completa de transacciones financieras
  - ✅ Comandos de control (crear cuentas, modificar balances, etc.)
  - ✅ Análisis financiero y consejos personalizados
  - ✅ Soporte multi-moneda (USD, EUR, COP, MXN, ARS, etc.)

#### **Frontend**
- **Reconocimiento de voz**: Web Speech API (navegador)
  - ⚠️ **Limitación**: Solo convierte voz a texto
  - ⚠️ **Limitación**: Dependencia del navegador (Chrome/Edge principalmente)
  - ⚠️ **Limitación**: No funciona en todos los navegadores
  - ⚠️ **Limitación**: Requiere conexión constante a internet
- **Síntesis de voz**: ❌ **No implementada**
- **Experiencia**: Unidireccional (usuario habla → transcribe → respuesta escrita)

### Funcionalidades Financieras Existentes

| Categoría | Funcionalidades |
|-----------|-----------------|
| **Transacciones** | Registrar ingresos, registrar gastos, eliminar transacciones, editar transacciones |
| **Cuentas** | Crear cuentas, renombrar cuentas, establecer balances, listar cuentas, consultar balances |
| **Categorías** | Listar categorías, crear categorías personalizadas, asignación automática |
| **Consultas** | Balance total, gastos del mes, ingresos del mes, análisis por categoría, transacciones recientes |
| **Análisis** | Estadísticas mensuales, tendencias de gasto, tasa de ahorro, consejos personalizados |
| **Transferencias** | Entre cuentas del usuario |
| **Multi-moneda** | Soporte para USD, EUR, COP, MXN, ARS, PEN, CLP, BRL |

### Limitaciones Identificadas

#### **Técnicas**
1. ❌ **Sin respuesta en voz**: Usuario debe leer respuestas en pantalla
2. ❌ **Sin conversación voz a voz**: Interacción no es fluida
3. ⚠️ **Dependencia del navegador**: Web Speech API no universal
4. ⚠️ **Sin soporte offline**: Requiere conexión constante
5. ⚠️ **Latencia variable**: Depende de la red y procesamiento

#### **Experiencia de Usuario**
1. ⚠️ **Barrera de accesibilidad**: Personas con discapacidad visual tienen dificultades
2. ⚠️ **No manos libres completo**: Requiere mirar pantalla para respuestas
3. ⚠️ **Curva de aprendizaje**: Usuario debe saber qué comandos decir
4. ⚠️ **Sin confirmación auditiva**: Usuario no sabe si el comando se ejecutó correctamente

---

## 🎯 Objetivos y Requisitos

### Objetivos Principales

1. **🎙️ Conversación Voz a Voz Completa**
   - Usuario habla → Sistema responde en voz
   - Experiencia natural y fluida
   - Sin necesidad de mirar pantalla

2. **💰 Control Total por Voz**
   - Todas las funciones financieras accesibles por voz
   - Confirmaciones auditivas de acciones críticas
   - Retroalimentación inmediata

3. **💵 Costo Operativo Mínimo**
   - Priorizar soluciones gratuitas
   - Modelos auto-hospedados cuando posible
   - Fallbacks económicos

4. **🚀 Experiencia Conversacional Natural**
   - No comandos rígidos
   - Comprensión del contexto
   - Manejo de ambigüedades y errores

### Requisitos Funcionales

#### **RF1: Reconocimiento de Voz (Speech-to-Text)**
- Soporte para múltiples idiomas (prioridad: español, inglés)
- Precisión > 90% en condiciones normales
- Latencia < 1 segundo
- Manejo de ruido ambiental moderado

#### **RF2: Procesamiento de Lenguaje Natural**
- Detección de intenciones (registrar gasto, consultar balance, etc.)
- Extracción de entidades (montos, fechas, categorías, cuentas)
- Manejo de contexto conversacional
- Corrección de errores de transcripción

#### **RF3: Síntesis de Voz (Text-to-Speech)**
- Voz natural y agradable
- Soporte para español (múltiples acentos)
- Latencia < 1 segundo
- Calidad mínima aceptable (no robótica)

#### **RF4: Gestión de Conversaciones**
- Mantener contexto entre interacciones
- Confirmaciones para acciones críticas
- Manejo de interrupciones
- Capacidad de deshacer/cancelar

#### **RF5: Funcionalidades Financieras por Voz**
- **Registrar transacciones**: "Gasté 50 mil pesos en supermercado"
- **Consultar balances**: "¿Cuál es mi balance?"
- **Análisis**: "¿Cuánto gasté este mes?"
- **Gestión de cuentas**: "Crea una cuenta llamada Ahorros"
- **Transferencias**: "Transfiere 100 de Efectivo a Banco"
- **Eliminar transacciones**: "Elimina la última compra de pizza"

### Requisitos No Funcionales

#### **RNF1: Performance**
- Latencia total (voz → respuesta en voz): < 3 segundos
- Procesamiento concurrente: Mínimo 10 usuarios simultáneos
- Disponibilidad: 99% uptime

#### **RNF2: Seguridad**
- Autenticación JWT mantenida
- No almacenar audio sin consentimiento
- Encriptación de datos sensibles

#### **RNF3: Escalabilidad**
- Arquitectura preparada para crecimiento
- Caché de respuestas comunes
- Rate limiting por usuario

#### **RNF4: Usabilidad**
- Experiencia intuitiva sin manual
- Feedback auditivo claro
- Manejo gracioso de errores

---

## 🤖 Modelos de IA Recomendados

### Estrategia: Arquitectura Híbrida de Costos

#### **Opción A: Solución 100% Gratuita (Recomendada para MVP)**

| Componente | Tecnología | Costo | Pros | Contras |
|------------|------------|-------|------|---------|
| **Speech-to-Text** | **OpenAI Whisper (local)** | **GRATIS** | ✅ Precisión excelente<br>✅ Soporte 99 idiomas<br>✅ Auto-hospedado<br>✅ Sin límites de uso | ⚠️ Requiere GPU (opcional)<br>⚠️ Latencia ~1-2s |
| **NLU** | **Groq Llama 3.3 70B** (actual) | **GRATIS** | ✅ Ya implementado<br>✅ Excelente comprensión<br>✅ Gratis con límites generosos | ⚠️ Límite de requests/día<br>⚠️ Dependencia externa |
| **Text-to-Speech** | **pyttsx3** (offline) | **GRATIS** | ✅ 100% offline<br>✅ Sin límites<br>✅ Múltiples voces | ⚠️ Calidad robótica<br>⚠️ Menos natural |
| **Alternativa TTS** | **gTTS** (Google TTS) | **GRATIS** | ✅ Calidad superior<br>✅ Voces naturales<br>✅ Fácil integración | ⚠️ Requiere internet<br>⚠️ Posible rate limiting |

**Estimación de Costo**: **$0/mes** (100% gratuito)

---

#### **Opción B: Solución Híbrida Económica (Mejor Calidad, Bajo Costo)**

| Componente | Tecnología | Costo Mensual | Pros | Contras |
|------------|------------|---------------|------|---------|
| **Speech-to-Text** | **OpenAI Whisper (local)** | **GRATIS** | ✅ Precisión excelente<br>✅ Auto-hospedado | ⚠️ Latencia ~1-2s |
| **NLU** | **Groq Llama 3.3 70B** | **GRATIS** | ✅ Ya implementado<br>✅ Excelente comprensión | ⚠️ Límites generosos pero no ilimitados |
| **Text-to-Speech** | **ElevenLabs Free Tier** | **GRATIS** (10k caracteres/mes) | ✅ Calidad premium<br>✅ Voces ultra-realistas<br>✅ Soporte español | ⚠️ Límite mensual<br>⚠️ Requiere cuenta |
| **TTS Fallback** | **Google Cloud TTS** | **~$4/millón caracteres** | ✅ Calidad excelente<br>✅ 1 millón gratis/mes<br>✅ Neural voices | ⚠️ Requiere cuenta GCP<br>⚠️ Pago después gratis |

**Estimación de Costo**: **$0-5/mes** (dependiendo uso)

---

#### **Opción C: Solución Profesional (Máxima Calidad)**

| Componente | Tecnología | Costo Mensual | Pros | Contras |
|------------|------------|---------------|------|---------|
| **Speech-to-Text** | **Google Speech-to-Text** | **GRATIS** (60 min/mes)<br>Luego $0.006/15s | ✅ Latencia baja<br>✅ Precisión superior<br>✅ Streaming | ⚠️ Costo variable<br>⚠️ Requiere cuenta |
| **NLU** | **Groq Llama 3.3 70B** | **GRATIS** | ✅ Ya implementado | ⚠️ Límites de requests |
| **Text-to-Speech** | **Azure Neural TTS** | **$15/1M caracteres**<br>500k gratis/mes | ✅ Calidad premium<br>✅ Voces naturales<br>✅ Baja latencia | ⚠️ Costo moderado<br>⚠️ Requiere cuenta Azure |

**Estimación de Costo**: **$5-20/mes** (500-2000 usuarios activos)

---

### 🏆 Recomendación Final

**Para arrancar (Fase 1): Opción A - Solución 100% Gratuita**

#### **Stack Tecnológico Recomendado**

```python
# Speech-to-Text
WHISPER_MODEL = "openai/whisper-medium"  # Balance precisión/velocidad
WHISPER_DEVICE = "cpu"  # Cambiar a "cuda" si hay GPU

# Natural Language Understanding
NLU_MODEL = "groq/llama-3.3-70b-versatile"  # Actual

# Text-to-Speech (Dual: calidad + fallback)
TTS_PRIMARY = "gTTS"  # Google TTS (calidad, gratis)
TTS_FALLBACK = "pyttsx3"  # Offline (siempre disponible)
TTS_LANGUAGE = "es"  # Español
TTS_ACCENT = "es-MX"  # Español México (o es-ES para España)
```

#### **Justificación**

1. **Whisper (local)**:
   - ✅ Gratis e ilimitado
   - ✅ Precisión comparable a servicios pagos
   - ✅ Soporte excelente para español
   - ✅ Modelo `medium` ofrece balance óptimo (377M parámetros)
   - ⏱️ Latencia aceptable en CPU (~1-2s para clips de 5-10s)

2. **Groq Llama 3.3**:
   - ✅ Ya integrado y funcionando
   - ✅ Comprensión excelente del español
   - ✅ Límite gratuito generoso (14,400 requests/día)
   - ✅ Baja latencia

3. **gTTS + pyttsx3 (Dual TTS)**:
   - ✅ gTTS: Calidad superior, voces naturales de Google
   - ✅ pyttsx3: Fallback offline si falla gTTS
   - ✅ Sin costos
   - ⚠️ gTTS tiene límites suaves (rate limiting), pero manejable

#### **Transición a Opción B (Fase 2)**

Cuando el producto crezca y necesite mejor calidad:
- Mantener Whisper local (gratis)
- Mantener Groq (gratis)
- **Upgrade TTS**: ElevenLabs (10k caracteres gratis/mes) → Calidad premium
- **Fallback**: Google Cloud TTS (1M caracteres gratis/mes) → Excelente calidad

**Costo estimado Fase 2**: $0-5/mes

---

## 🏗️ Arquitectura Propuesta

### Diagrama de Arquitectura

```
┌─────────────────────────────────────────────────────────────────┐
│                        CLIENTE (Frontend)                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────┐      ┌──────────────┐      ┌──────────────┐ │
│  │  Micrófono   │─────▶│  Audio       │─────▶│   WebSocket  │ │
│  │  (Captura)   │      │  Preprocessor│      │   Client     │ │
│  └──────────────┘      └──────────────┘      └──────┬───────┘ │
│                                                      │          │
│                                              ┌───────▼────────┐ │
│  ┌──────────────┐      ┌──────────────┐     │   HTTP Client │ │
│  │  Speaker     │◀─────│   Audio      │◀────│   (Fallback)  │ │
│  │  (Playback)  │      │   Player     │     └───────┬────────┘ │
│  └──────────────┘      └──────────────┘             │          │
│                                                      │          │
└──────────────────────────────────────────────────────┼──────────┘
                                                       │
                                    Internet           │
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┿━━━━━━━━━
                                                       │
┌──────────────────────────────────────────────────────┼──────────┐
│                    BACKEND (Flask)                   │          │
├──────────────────────────────────────────────────────┼──────────┤
│                                                      │          │
│  ┌────────────────────────────────────────────────┐ │          │
│  │          WebSocket Server (Socket.IO)          │ │          │
│  │  - Gestión de conexiones en tiempo real        │◀┘          │
│  │  - Streaming de audio bidireccional             │            │
│  └────────────────┬───────────────────────────────┬─┘            │
│                   │                               │              │
│  ┌────────────────▼──────────┐  ┌────────────────▼─────────┐   │
│  │   Speech-to-Text Service  │  │  Text-to-Speech Service  │   │
│  │   - Whisper (local)       │  │  - gTTS (primary)        │   │
│  │   - Audio preprocessing   │  │  - pyttsx3 (fallback)    │   │
│  │   - Language detection    │  │  - Audio caching         │   │
│  └────────────────┬──────────┘  └────────────────▲─────────┘   │
│                   │                               │              │
│                   │       ┌───────────────────────┘              │
│                   │       │                                      │
│  ┌────────────────▼───────┴───────────────────────────────┐    │
│  │             NLU & Conversation Manager                  │    │
│  │  - Detección de intenciones (Groq Llama 3.3)          │    │
│  │  - Extracción de entidades                             │    │
│  │  - Gestión de contexto conversacional                  │    │
│  │  - Confirmaciones para acciones críticas               │    │
│  └────────────────┬───────────────────────────────────────┘    │
│                   │                                             │
│  ┌────────────────▼───────────────────────────────────────┐    │
│  │           Financial Operations Handler                  │    │
│  │  - Transaction Manager (create, delete, edit)          │    │
│  │  - Account Manager (create, rename, balance)           │    │
│  │  - Query Engine (balance, stats, analysis)             │    │
│  │  - Transfer Manager                                    │    │
│  └────────────────┬───────────────────────────────────────┘    │
│                   │                                             │
│  ┌────────────────▼───────────────────────────────────────┐    │
│  │                  Database Layer                         │    │
│  │  - SQLAlchemy ORM                                       │    │
│  │  - Models: User, Transaction, Account, Category, Chat  │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Flujo de Interacción Voz a Voz

```
Usuario Habla → [1] Captura Audio → [2] Envío al Backend (WebSocket/HTTP)
                                              ↓
                                    [3] Speech-to-Text (Whisper)
                                              ↓
                                    [4] Transcripción a Texto
                                              ↓
                                    [5] NLU: Detección Intención + Entidades
                                              ↓
                                    [6] Ejecución de Operación Financiera
                                              ↓
                                    [7] Generación de Respuesta (Groq)
                                              ↓
                                    [8] Text-to-Speech (gTTS/pyttsx3)
                                              ↓
                                    [9] Envío Audio al Cliente
                                              ↓
← Usuario Escucha ← [10] Reproducción de Audio
```

#### **Optimizaciones de Latencia**

1. **Pipeline Paralelo**: Mientras TTS genera audio, siguiente intención se procesa
2. **Streaming**: Audio se envía en chunks, no esperar archivo completo
3. **Caché**: Respuestas comunes pre-generadas en audio
4. **Predicción**: Pre-cargar respuestas probables durante conversación

---

### Componentes Clave

#### **1. Voice Input Service (Frontend + Backend)**

**Frontend (`voice-chat-interface.js`)**
```javascript
// Captura de audio con calidad optimizada
const audioStream = await navigator.mediaDevices.getUserMedia({
  audio: {
    echoCancellation: true,
    noiseSuppression: true,
    autoGainControl: true,
    sampleRate: 16000  // Whisper optimal
  }
});

// Envío a backend (WebSocket para tiempo real)
const socket = io('/voice-chat');
socket.emit('audio-chunk', audioChunk);

// Recepción de respuesta en audio
socket.on('audio-response', (audioData) => {
  playAudio(audioData);
});
```

**Backend (`voice_service.py`)**
```python
import whisper
import torch

class VoiceInputService:
    def __init__(self):
        # Cargar modelo Whisper (medium = balance precisión/velocidad)
        self.model = whisper.load_model("medium")
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
    
    def transcribe(self, audio_file_path):
        """Transcribe audio a texto"""
        result = self.model.transcribe(
            audio_file_path,
            language="es",  # Español
            task="transcribe",
            fp16=False  # CPU safe
        )
        return result["text"]
    
    def transcribe_with_metadata(self, audio_file_path):
        """Transcribe con información adicional"""
        result = self.model.transcribe(
            audio_file_path,
            language="es",
            task="transcribe",
            word_timestamps=True,  # Timestamps de palabras
            condition_on_previous_text=True  # Contexto
        )
        return {
            'text': result["text"],
            'language': result["language"],
            'segments': result["segments"],
            'confidence': self._calculate_confidence(result)
        }
```

---

#### **2. Text-to-Speech Service (`tts_service.py`)**

```python
from gtts import gTTS
import pyttsx3
import os
from pathlib import Path
import hashlib

class TTSService:
    def __init__(self):
        self.cache_dir = Path("instance/audio_cache")
        self.cache_dir.mkdir(exist_ok=True, parents=True)
        
        # Configurar fallback offline
        self.offline_engine = pyttsx3.init()
        self.offline_engine.setProperty('rate', 150)  # Velocidad
        self.offline_engine.setProperty('volume', 0.9)
        
        # Obtener voces en español (si disponible)
        voices = self.offline_engine.getProperty('voices')
        spanish_voice = next((v for v in voices if 'spanish' in v.name.lower()), voices[0])
        self.offline_engine.setProperty('voice', spanish_voice.id)
    
    def synthesize(self, text, use_cache=True):
        """
        Genera audio a partir de texto
        Retorna: ruta al archivo de audio
        """
        # Verificar caché
        if use_cache:
            cached_file = self._get_cached_audio(text)
            if cached_file:
                return cached_file
        
        # Intentar gTTS (calidad superior)
        try:
            return self._synthesize_gtts(text)
        except Exception as e:
            print(f"gTTS falló: {e}. Usando fallback offline...")
            return self._synthesize_offline(text)
    
    def _synthesize_gtts(self, text):
        """Síntesis con Google TTS (online)"""
        file_path = self.cache_dir / f"{self._text_hash(text)}.mp3"
        
        tts = gTTS(text=text, lang='es', tld='com.mx', slow=False)
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
        file_path = self.cache_dir / f"{self._text_hash(text)}.mp3"
        if file_path.exists():
            return file_path
        
        # Intentar versión offline
        file_path_offline = self.cache_dir / f"{self._text_hash(text)}_offline.mp3"
        if file_path_offline.exists():
            return file_path_offline
        
        return None
    
    def _text_hash(self, text):
        """Genera hash único para texto"""
        return hashlib.md5(text.encode()).hexdigest()
    
    def clear_cache(self, max_age_days=7):
        """Limpia caché antiguo"""
        import time
        cutoff = time.time() - (max_age_days * 86400)
        
        for file in self.cache_dir.glob("*.mp3"):
            if file.stat().st_mtime < cutoff:
                file.unlink()
```

---

#### **3. NLU & Conversation Manager (`conversation_manager.py`)**

```python
from services.ai_service import ai_service
from models import db, ChatMessage
from datetime import datetime

class ConversationManager:
    def __init__(self):
        self.ai_service = ai_service
        self.context_window = 10  # Últimos 10 mensajes
    
    def process_voice_input(self, user_id, transcribed_text):
        """
        Procesa input de voz y genera respuesta
        Retorna: {'text': str, 'audio_path': str, 'action': dict}
        """
        # 1. Guardar mensaje del usuario
        user_message = ChatMessage(
            user_id=user_id,
            role='user',
            content=transcribed_text,
            message_metadata={'input_type': 'voice'}
        )
        db.session.add(user_message)
        db.session.commit()
        
        # 2. Obtener contexto conversacional
        conversation_history = self._get_conversation_history(user_id)
        
        # 3. Procesar con IA (Groq)
        response = self.ai_service.chat(
            user_id=user_id,
            message=transcribed_text,
            conversation_history=conversation_history
        )
        
        # 4. Detectar si requiere confirmación
        requires_confirmation = self._check_confirmation_needed(response)
        
        # 5. Guardar respuesta
        assistant_message = ChatMessage(
            user_id=user_id,
            role='assistant',
            content=response,
            message_metadata={
                'input_type': 'voice',
                'requires_confirmation': requires_confirmation
            }
        )
        db.session.add(assistant_message)
        db.session.commit()
        
        # 6. Generar audio de respuesta
        from services.tts_service import tts_service
        audio_path = tts_service.synthesize(response)
        
        return {
            'text': response,
            'audio_path': str(audio_path),
            'requires_confirmation': requires_confirmation,
            'message_id': assistant_message.id
        }
    
    def _get_conversation_history(self, user_id):
        """Obtiene historial reciente de conversación"""
        messages = ChatMessage.query.filter_by(user_id=user_id).order_by(
            ChatMessage.created_at.desc()
        ).limit(self.context_window).all()
        
        return [
            {'role': m.role, 'content': m.content}
            for m in reversed(messages)
        ]
    
    def _check_confirmation_needed(self, response):
        """Detecta si la respuesta requiere confirmación del usuario"""
        confirmation_keywords = [
            'confirmar', 'confirmación', '¿estás seguro?',
            'confirma esta acción', 'requiere confirmación'
        ]
        return any(kw in response.lower() for kw in confirmation_keywords)
```

---

#### **4. WebSocket Handler (`socketio_handlers.py`)**

```python
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask import request
from utils.jwt_utils import decode_token
import base64
from pathlib import Path
import uuid

socketio = SocketIO()

# Instancias de servicios
from services.voice_service import voice_service
from services.conversation_manager import conversation_manager

@socketio.on('connect', namespace='/voice-chat')
def handle_connect():
    """Cliente se conecta al chat de voz"""
    # Autenticar con JWT
    token = request.args.get('token')
    if not token:
        return False  # Rechazar conexión
    
    try:
        payload = decode_token(token)
        user_id = payload['user_id']
        join_room(f'user_{user_id}')
        emit('connected', {'status': 'ready'})
    except Exception as e:
        print(f"Authentication error: {e}")
        return False

@socketio.on('audio-chunk', namespace='/voice-chat')
def handle_audio_chunk(data):
    """Recibe chunk de audio del cliente"""
    # Obtener user_id de la sesión
    token = request.args.get('token')
    payload = decode_token(token)
    user_id = payload['user_id']
    
    # Guardar audio temporalmente
    audio_data = base64.b64decode(data['audio'])
    temp_file = Path(f"instance/temp/audio_{uuid.uuid4()}.wav")
    temp_file.parent.mkdir(exist_ok=True, parents=True)
    temp_file.write_bytes(audio_data)
    
    # Emitir estado: procesando
    emit('status', {'state': 'transcribing'})
    
    try:
        # 1. Speech-to-Text
        transcription = voice_service.transcribe(str(temp_file))
        emit('transcription', {'text': transcription})
        
        # 2. Procesar con IA
        emit('status', {'state': 'thinking'})
        result = conversation_manager.process_voice_input(user_id, transcription)
        
        # 3. Enviar respuesta en texto y audio
        emit('status', {'state': 'responding'})
        
        # Leer audio generado
        with open(result['audio_path'], 'rb') as f:
            audio_response = base64.b64encode(f.read()).decode('utf-8')
        
        emit('response', {
            'text': result['text'],
            'audio': audio_response,
            'requires_confirmation': result['requires_confirmation']
        })
        
        emit('status', {'state': 'ready'})
        
    except Exception as e:
        print(f"Error processing audio: {e}")
        import traceback
        traceback.print_exc()
        emit('error', {'message': 'Error procesando audio'})
    
    finally:
        # Limpiar archivo temporal
        if temp_file.exists():
            temp_file.unlink()

@socketio.on('disconnect', namespace='/voice-chat')
def handle_disconnect():
    """Cliente se desconecta"""
    print('Client disconnected')
```

---

## 🗣️ Mapeo de Funciones Financieras a Comandos de Voz

### Matriz de Comandos de Voz

| Función | Comandos de Voz Naturales | Entidades a Extraer | Confirmación |
|---------|---------------------------|---------------------|--------------|
| **Registrar Gasto** | • "Gasté 50 mil en supermercado"<br>• "Compré pizza por 35 dólares ayer"<br>• "Pagué 200 de gasolina con mi tarjeta" | - Monto<br>- Categoría<br>- Fecha (opcional)<br>- Cuenta (opcional) | ❌ No (< $100)<br>✅ Sí (≥ $100) |
| **Registrar Ingreso** | • "Me pagaron 800 del trabajo"<br>• "Recibí 150 de Juan por la renta"<br>• "Ingreso de 2000 en mi cuenta Ahorros" | - Monto<br>- Descripción<br>- Cuenta (opcional)<br>- Fecha (opcional) | ❌ No |
| **Consultar Balance** | • "¿Cuál es mi balance?"<br>• "¿Cuánto dinero tengo?"<br>• "Dime mi balance total" | - Ninguna | ❌ No |
| **Consultar Gastos Mes** | • "¿Cuánto gasté este mes?"<br>• "Muéstrame mis gastos de febrero"<br>• "¿En qué gasté este mes?" | - Periodo (mes/año) | ❌ No |
| **Consultar Ingresos Mes** | • "¿Cuánto gané este mes?"<br>• "Mis ingresos de enero" | - Periodo | ❌ No |
| **Análisis por Categoría** | • "¿En qué categoría gasto más?"<br>• "Muéstrame gastos de comida"<br>• "¿Cuánto llevo en transporte?" | - Categoría (opcional) | ❌ No |
| **Crear Cuenta** | • "Crea una cuenta llamada Nequi"<br>• "Nueva cuenta Ahorros con 500 dólares"<br>• "Agregar cuenta de efectivo" | - Nombre<br>- Saldo inicial (opcional)<br>- Tipo (opcional) | ✅ Sí |
| **Renombrar Cuenta** | • "Cambia el nombre de cuenta 2 a Bolsillo"<br>• "Renombra Efectivo a Cartera" | - Identificador (nombre o #)<br>- Nuevo nombre | ✅ Sí |
| **Transferencia** | • "Transfiere 100 de Efectivo a Banco"<br>• "Mueve 50 dólares a Ahorros" | - Monto<br>- Cuenta origen<br>- Cuenta destino | ✅ Sí |
| **Eliminar Transacción** | • "Elimina la última compra de pizza"<br>• "Borra el gasto de 35 dólares de ayer"<br>• "Cancela la transacción de gasolina" | - Identificador (descripción, monto, fecha) | ✅ Sí |
| **Ver Transacciones Recientes** | • "Muéstrame mis últimas transacciones"<br>• "¿Qué gastos hice esta semana?" | - Periodo (opcional) | ❌ No |
| **Consejos Financieros** | • "Dame consejos para ahorrar"<br>• "¿Cómo puedo mejorar mis finanzas?"<br>• "Ayúdame a crear un presupuesto" | - Ninguna | ❌ No |
| **Establecer Balance** | • "Establece el balance de Efectivo en 500"<br>• "Cambia mi saldo a 1000 dólares" | - Cuenta<br>- Nuevo balance | ✅✅ Sí (Doble) |

---

### Flujo de Confirmación para Acciones Críticas

```
Usuario: "Elimina la última compra de pizza"
           ↓
Sistema (Voz): "Encontré esta transacción:
                Pizza - $35 dólares - 1 de marzo - Cuenta Efectivo
                ¿Quieres eliminarla? Di SÍ para confirmar o NO para cancelar"
           ↓
Usuario: "Sí"
           ↓
Sistema (Voz): "Listo. Transacción eliminada. Tu nuevo balance en Efectivo es $465"
```

---

### Prompt Engineering para Detección de Intenciones

**Ejemplo de Prompt al Modelo (Groq Llama 3.3)**

```python
VOICE_INTENT_PROMPT = f"""Eres un asistente financiero que procesa comandos de voz.

CONTEXTO DEL USUARIO:
{user_context}

COMANDO DE VOZ DEL USUARIO:
"{transcribed_text}"

TAREA:
1. Identifica la INTENCIÓN principal del usuario
2. Extrae ENTIDADES relevantes (montos, fechas, cuentas, categorías)
3. Genera una RESPUESTA CONVERSACIONAL en voz

INTENCIONES POSIBLES:
- REGISTRAR_GASTO: Usuario quiere registrar un gasto
- REGISTRAR_INGRESO: Usuario quiere registrar un ingreso
- CONSULTAR_BALANCE: Usuario pregunta por su balance
- CONSULTAR_GASTOS_MES: Usuario pregunta cuánto gastó
- CONSULTAR_INGRESOS_MES: Usuario pregunta cuánto ganó
- ANALISIS_CATEGORIA: Usuario pregunta por categoría específica
- CREAR_CUENTA: Usuario quiere crear una cuenta nueva
- RENOMBRAR_CUENTA: Usuario quiere renombrar una cuenta
- TRANSFERENCIA: Usuario quiere transferir dinero
- ELIMINAR_TRANSACCION: Usuario quiere eliminar una transacción
- CONSULTAR_TRANSACCIONES: Usuario quiere ver sus transacciones
- CONSEJOS: Usuario pide consejos financieros
- CONVERSACION: Usuario solo conversa (no acción financiera)

FORMATO DE RESPUESTA (JSON):
{{
  "intent": "NOMBRE_INTENCION",
  "entities": {{
    "amount": 123.45,
    "category": "Comida",
    "account": "Efectivo",
    "date": "2026-03-01",
    "description": "Pizza"
  }},
  "requires_confirmation": true/false,
  "response_text": "Texto conversacional para decir en voz",
  "confidence": 0.95
}}

REGLAS IMPORTANTES:
- Si detectas un monto, extráelo en la moneda del usuario ({currency})
- Si falta información crítica, pregunta al usuario
- Si la intención no es clara, pide aclaración
- Genera respuestas CORTAS y NATURALES para voz (máximo 3-4 oraciones)
- NO uses formato markdown en response_text (será hablado)
- Para acciones destructivas (eliminar, transferir), requires_confirmation = true
"""
```

---

### Ejemplo de Conversación Completa

```
👤 Usuario: [Presiona botón de micrófono]

🤖 Sistema (visual): 🎙️ Escuchando...

👤 Usuario (voz): "Hola, ¿cuánto dinero tengo?"

🤖 Sistema (visual): 💬 Procesando...
🤖 Sistema (voz): "Hola Francisco. Tu balance total es de 1,250 dólares. 
                   Tienes 450 en Efectivo, 600 en Banco y 200 en Ahorros. 
                   ¿Necesitas algo más?"

👤 Usuario (voz): "Sí, registra un gasto de 50 dólares en supermercado"

🤖 Sistema (visual): ✅ Registro completado
🤖 Sistema (voz): "Perfecto. Registré 50 dólares en la categoría Supermercado 
                   desde tu cuenta Efectivo. Te quedan 400 dólares en Efectivo. 
                   Tu balance total ahora es 1,200 dólares."

👤 Usuario (voz): "¿Cuánto gasté este mes?"

🤖 Sistema (voz): "Este mes has gastado un total de 1,350 dólares. 
                   Las categorías con más gasto son: 
                   Supermercado 450 dólares, 
                   Transporte 300 dólares, 
                   y Restaurantes 250 dólares. 
                   Has gastado el 90% de tus ingresos este mes. 
                   ¿Quieres consejos para reducirlo?"

👤 Usuario (voz): "Sí, dame consejos"

🤖 Sistema (voz): "Basándome en tus gastos, te recomiendo: 
                   Primero, reducir gastos en restaurantes, actualmente 250 dólares. 
                   Podrías ahorrar 100 cocinando más en casa. 
                   Segundo, considera usar transporte público o compartir viajes 
                   para reducir el gasto de 300 dólares en transporte. 
                   Con estos cambios podrías ahorrar hasta 150 dólares al mes."

👤 Usuario (voz): "Gracias"

🤖 Sistema (voz): "De nada. Estoy aquí para ayudarte. ¿Algo más?"

👤 Usuario (voz): "No, eso es todo"

🤖 Sistema (voz): "Perfecto. Que tengas un excelente día."
```

---

## 🛠️ Stack Tecnológico

### Backend

| Componente | Tecnología | Versión | Propósito |
|------------|------------|---------|-----------|
| **Framework** | Flask | 3.0+ | API REST + WebSocket |
| **WebSocket** | Flask-SocketIO | 5.3+ | Comunicación tiempo real |
| **Speech-to-Text** | OpenAI Whisper | 20231117 | Transcripción de voz |
| **Text-to-Speech** | gTTS | 2.5+ | Síntesis de voz (primario) |
| **TTS Fallback** | pyttsx3 | 2.90+ | Síntesis offline |
| **NLU** | Groq API (Llama 3.3) | - | Procesamiento lenguaje natural |
| **ORM** | SQLAlchemy | 2.0+ | Persistencia de datos |
| **Database** | SQLite | 3.0+ | Base de datos |
| **Audio Processing** | pydub | 0.25+ | Manipulación de audio |
| **Auth** | JWT (PyJWT) | 2.8+ | Autenticación |

### Frontend

| Componente | Tecnología | Propósito |
|------------|------------|-----------|
| **WebSocket Client** | Socket.IO Client | 4.6+ | Conexión con backend |
| **Audio API** | Web Audio API | - | Captura/reproducción audio |
| **UI Framework** | Vanilla JS | - | Interface de usuario |
| **CSS Framework** | Custom CSS | - | Estilos |

### Infraestructura

| Componente | Tecnología | Propósito |
|------------|------------|-----------|
| **Servidor** | Gunicorn | Producción WSGI |
| **Proxy** | Nginx (opcional) | Reverse proxy |
| **Hosting** | Auto-hospedado / VPS | Deployment |
| **Monitoreo** | Python logging | Logs y debugging |

---

## 🔧 Consideraciones de Implementación

### 1. Performance y Optimización

#### **A. Latencia de Speech-to-Text (Whisper)**

**Problema**: Modelo `medium` de Whisper toma ~1-2s en CPU para audio de 5-10s

**Soluciones**:
1. **Usar modelo `small` para latencia ultra-baja**
   ```python
   # medium: 377M parámetros, ~1-2s latencia
   # small: 244M parámetros, ~0.5-1s latencia (90% precisión de medium)
   model = whisper.load_model("small")  # Más rápido, buena precisión
   ```

2. **Procesamiento en GPU** (si disponible)
   ```python
   device = "cuda" if torch.cuda.is_available() else "cpu"
   model = whisper.load_model("medium", device=device)
   # GPU: ~0.2-0.5s para mismo audio
   ```

3. **Pre-procesamiento de audio**
   ```python
   # Reducir tamaño de audio sin perder calidad
   from pydub import AudioSegment
   audio = AudioSegment.from_file(audio_path)
   audio = audio.set_frame_rate(16000)  # Whisper optimal
   audio = audio.set_channels(1)  # Mono
   ```

4. **Streaming VAD (Voice Activity Detection)**
   ```python
   # Detectar cuando usuario terminó de hablar para empezar transcripción
   # No esperar a que presione botón "stop"
   import webrtcvad
   vad = webrtcvad.Vad(2)  # Aggressiveness level
   ```

#### **B. Latencia de Text-to-Speech**

**Problema**: gTTS requiere llamada de red (~500ms-1s)

**Soluciones**:
1. **Caché agresivo de respuestas comunes**
   ```python
   # Pre-generar y cachear respuestas frecuentes
   COMMON_RESPONSES = [
       "¿En qué puedo ayudarte?",
       "Listo, registrado exitosamente",
       "Tu balance total es {balance}",
       # ...50+ respuestas comunes
   ]
   
   # Pre-generar al iniciar servidor
   for response in COMMON_RESPONSES:
       tts_service.synthesize(response, use_cache=True)
   ```

2. **Síntesis en paralelo con procesamiento**
   ```python
   import threading
   
   # Mientras AI genera respuesta, pre-iniciar TTS
   def async_synthesize(text):
       thread = threading.Thread(target=tts_service.synthesize, args=(text,))
       thread.start()
       return thread
   ```

3. **Streaming de audio** (avanzado)
   ```python
   # Enviar audio en chunks mientras se genera
   def stream_tts(text):
       sentences = text.split('. ')
       for sentence in sentences:
           audio_chunk = tts_service.synthesize(sentence)
           yield audio_chunk  # Enviar inmediatamente
   ```

#### **C. Optimización de Groq API**

**Problema**: Límite de 14,400 requests/día (gratis)

**Soluciones**:
1. **Caché de respuestas similares**
   ```python
   from rapidfuzz import fuzz
   
   # Si pregunta es muy similar a una anterior (>90%), reusar respuesta
   if fuzz.ratio(new_question, cached_question) > 90:
       return cached_response
   ```

2. **Rate limiting por usuario**
   ```python
   # Máximo 100 requests/día por usuario
   USER_DAILY_LIMIT = 100
   ```

3. **Respuestas template para consultas simples**
   ```python
   # No usar IA para consultas directas de datos
   if intent == "CONSULTAR_BALANCE":
       # Generar respuesta directamente sin IA
       return f"Tu balance total es {balance} {currency}"
   ```

---

### 2. Manejo de Errores y Fallbacks

#### **Cadena de Fallbacks**

```python
def process_voice_with_fallbacks(audio_path, user_id):
    """Procesa voz con múltiples fallbacks"""
    
    # 1. Intentar Whisper local
    try:
        transcription = whisper_service.transcribe(audio_path)
    except Exception as e:
        print(f"Whisper failed: {e}")
        
        # FALLBACK 1: Web Speech API (si cliente lo soporta)
        return {'error': 'whisper_failed', 'fallback': 'use_web_speech'}
    
    # 2. Procesar con Groq
    try:
        response = ai_service.chat(user_id, transcription)
    except Exception as e:
        print(f"Groq failed: {e}")
        
        # FALLBACK 2: Respuestas locales para intenciones simples
        response = detect_intent_locally(transcription)
        if not response:
            response = "Lo siento, hubo un error procesando tu solicitud. Inténtalo de nuevo."
    
    # 3. Sintetizar voz
    try:
        audio_file = gtts_service.synthesize(response)
    except Exception as e:
        print(f"gTTS failed: {e}")
        
        # FALLBACK 3: TTS offline
        audio_file = pyttsx3_service.synthesize(response)
    
    return {'transcription': transcription, 'response': response, 'audio': audio_file}
```

---

### 3. Seguridad y Privacidad

#### **A. Protección de Datos de Voz**

```python
# NO almacenar audio sin consentimiento explícito
STORE_AUDIO = os.environ.get('STORE_VOICE_RECORDINGS', 'false').lower() == 'true'

if STORE_AUDIO and user.consented_to_recording:
    # Solo si usuario dio consentimiento explícito
    save_audio(audio_path, user_id)
else:
    # Eliminar audio después de procesarlo
    os.unlink(audio_path)
```

#### **B. Autenticación en WebSocket**

```python
@socketio.on('connect', namespace='/voice-chat')
def handle_connect():
    token = request.args.get('token')
    
    # Validar JWT
    try:
        payload = decode_token(token)
        user_id = payload['user_id']
        
        # Verificar que token no esté expirado
        if payload['exp'] < time.time():
            return False
        
        # Guardar user_id en sesión
        session['user_id'] = user_id
        return True
        
    except Exception as e:
        print(f"Auth error: {e}")
        return False
```

#### **C. Rate Limiting**

```python
from flask_limiter import Limiter

limiter = Limiter(
    app,
    key_func=lambda: session.get('user_id'),
    default_limits=["200 per day", "50 per hour"]
)

@app.route('/api/voice/process', methods=['POST'])
@limiter.limit("30 per minute")  # Máximo 30 comandos de voz por minuto
def process_voice():
    # ...
```

---

### 4. Escalabilidad

#### **A. Procesamiento Asíncrono**

```python
from celery import Celery

celery = Celery('voice_tasks', broker='redis://localhost:6379')

@celery.task
def process_voice_async(audio_path, user_id):
    """Procesa voz en background"""
    transcription = whisper_service.transcribe(audio_path)
    response = conversation_manager.process(user_id, transcription)
    audio_file = tts_service.synthesize(response['text'])
    
    # Notificar al cliente via WebSocket
    socketio.emit('response', response, room=f'user_{user_id}')
```

#### **B. Caché Distribuido**

```python
import redis

redis_client = redis.Redis(host='localhost', port=6379, db=0)

def get_cached_audio(text):
    """Busca audio en Redis"""
    cache_key = f"audio:{hashlib.md5(text.encode()).hexdigest()}"
    audio_data = redis_client.get(cache_key)
    
    if audio_data:
        return audio_data
    return None

def cache_audio(text, audio_data):
    """Guarda audio en Redis (24h TTL)"""
    cache_key = f"audio:{hashlib.md5(text.encode()).hexdigest()}"
    redis_client.setex(cache_key, 86400, audio_data)  # 24 horas
```

---

### 5. Accesibilidad

#### **A. Soporte Multi-idioma**

```python
# Detección automática de idioma usuario
user_language = user.preferred_language or 'es'

# Whisper: Transcripción en idioma detectado
result = whisper_model.transcribe(audio, language=user_language)

# TTS: Síntesis en idioma del usuario
tts = gTTS(text=response, lang=user_language)
```

#### **B. Velocidad de Voz Ajustable**

```python
# Permitir al usuario ajustar velocidad de respuestas
user_tts_speed = user.tts_speed_preference or 1.0  # 0.5 - 2.0

# pyttsx3 (offline)
engine.setProperty('rate', 150 * user_tts_speed)

# gTTS: Usar parámetro 'slow=True' para velocidad reducida
tts = gTTS(text, lang='es', slow=(user_tts_speed < 0.8))
```

#### **C. Transcripción Visible**

```python
# Siempre mostrar transcripción en pantalla
# Beneficia a usuarios con problemas auditivos
response_data = {
    'audio': audio_base64,
    'text': response_text,  # Siempre incluir texto
    'transcription': user_transcription  # Lo que dijo el usuario
}
```

---

## 📅 Plan de Implementación por Fases

### **Fase 1: Fundamentos (Semanas 1-2)** ✅

#### Objetivos
- Configurar Speech-to-Text con Whisper
- Configurar Text-to-Speech básico
- Prueba de concepto voz a voz

#### Tareas

**Backend**
- [ ] Instalar dependencias (`whisper`, `gTTS`, `pyttsx3`)
- [ ] Crear servicio `voice_service.py` (Whisper STT)
- [ ] Crear servicio `tts_service.py` (gTTS + pyttsx3 fallback)
- [ ] Endpoint de prueba: `/api/voice/test` (enviar audio → recibir audio)
- [ ] Tests unitarios de servicios

**Frontend**
- [ ] Crear interfaz básica de captura de audio
- [ ] Implementar envío de audio a backend
- [ ] Reproducción de audio de respuesta
- [ ] Indicador visual de estado (grabando, procesando, hablando)

**Infraestructura**
- [ ] Configurar carpetas temporales para audio
- [ ] Script de limpieza de archivos temporales
- [ ] Variables de entorno para configuración

**Pruebas**
- [ ] Grabar audio de 5s → Verificar transcripción correcta
- [ ] Enviar texto → Verificar audio generado
- [ ] Latencia total < 5s

**Entregable**: Sistema básico que convierte voz a texto y genera respuesta en voz

---

### **Fase 2: Integración con NLU (Semanas 3-4)** 🎯

#### Objetivos
- Conectar voz con sistema de IA existente (Groq)
- Implementar gestión de contexto conversacional
- Soportar intenciones financieras básicas

#### Tareas

**Backend**
- [ ] Crear `conversation_manager.py`
- [ ] Integrar Whisper → Groq → TTS pipeline completo
- [ ] Implementar detección de intenciones
- [ ] Soporte para 5 intenciones básicas:
  - Consultar balance
  - Registrar gasto
  - Registrar ingreso
  - Consultar gastos del mes
  - Conversación general
- [ ] Guardar conversaciones de voz en base de datos

**Frontend**
- [ ] Mostrar transcripción en tiempo real
- [ ] Mostrar respuesta en texto + audio
- [ ] Botón de cancelar durante grabación
- [ ] Botón de repetir última respuesta

**Prompt Engineering**
- [ ] Diseñar prompt para detección de intenciones
- [ ] Diseñar prompt para extracción de entidades
- [ ] Optimizar respuestas para voz (cortas, naturales)

**Pruebas**
- [ ] Test: "¿Cuál es mi balance?" → Respuesta correcta en voz
- [ ] Test: "Gasté 50 en comida" → Transacción registrada + confirmación
- [ ] Test: Conversación de 5 turnos con contexto

**Entregable**: Chat de voz funcional con operaciones financieras básicas

---

### **Fase 3: Funcionalidades Completas (Semanas 5-6)** 🚀

#### Objetivos
- Soportar TODAS las funciones financieras por voz
- Implementar confirmaciones para acciones críticas
- Optimizar experiencia conversacional

#### Tareas

**Backend**
- [ ] Implementar 12 intenciones completas (ver tabla de mapeo)
- [ ] Sistema de confirmación para acciones destructivas
- [ ] Manejo de ambigüedades ("¿A qué cuenta te refieres?")
- [ ] Corrección de errores de transcripción
- [ ] Extracción avanzada de entidades (fechas relativas, categorías aproximadas)

**Frontend**
- [ ] UI para confirmaciones ("Di SÍ o NO")
- [ ] Historial de conversación de voz
- [ ] Botón "Deshacer última acción"
- [ ] Configuración: idioma, velocidad de voz

**Optimización**
- [ ] Caché de respuestas comunes (50+ frases)
- [ ] Pre-generación de audio para confirmaciones estándar
- [ ] Reducir latencia a < 3s

**Pruebas**
- [ ] Test suite completo (30+ escenarios)
- [ ] Test de flujo de confirmación
- [ ] Test de manejo de errores
- [ ] Test de contexto multi-turno

**Entregable**: Sistema de voz completo con todas las funciones

---

### **Fase 4: WebSocket y Tiempo Real (Semana 7)** ⚡

#### Objetivos
- Implementar comunicación WebSocket para mejor UX
- Reducir latencia con streaming
- Soporte para múltiples usuarios simultáneos

#### Tareas

**Backend**
- [ ] Instalar `flask-socketio`
- [ ] Crear `socketio_handlers.py`
- [ ] Implementar namespace `/voice-chat`
- [ ] Autenticación JWT en WebSocket
- [ ] Gestión de salas por usuario

**Frontend**
- [ ] Migrar de HTTP a WebSocket
- [ ] Implementar reconexión automática
- [ ] Indicadores de estado en tiempo real
- [ ] Manejo de desconexiones

**Optimización**
- [ ] Envío de audio en chunks (streaming)
- [ ] Procesamiento paralelo cuando posible
- [ ] Caché en Redis para usuarios concurrentes

**Pruebas**
- [ ] Test de 10 usuarios concurrentes
- [ ] Test de desconexión y reconexión
- [ ] Test de latencia con WebSocket vs HTTP

**Entregable**: Sistema de voz en tiempo real con latencia optimizada

---

### **Fase 5: Refinamiento y Producción (Semana 8)** 🎨

#### Objetivos
- Pulir experiencia de usuario
- Optimizar performance
- Preparar para producción

#### Tareas

**UX/UI**
- [ ] Animaciones de interfaz de voz
- [ ] Feedback auditivo (beeps, tonos)
- [ ] Tutorial interactivo de voz ("Di: 'Ayuda'")
- [ ] Dark mode compatible

**Performance**
- [ ] Profiling de latencia (identificar cuellos de botella)
- [ ] Optimizar modelo Whisper (small vs medium)
- [ ] Batch processing cuando posible
- [ ] Compresión de audio

**Monitoreo**
- [ ] Logging detallado de conversaciones
- [ ] Métricas: latencia, tasa de error, uso
- [ ] Dashboard de estadísticas

**Seguridad**
- [ ] Rate limiting robusto
- [ ] Validación de tamaño de audio
- [ ] Sanitización de inputs
- [ ] HTTPS obligatorio

**Documentación**
- [ ] README actualizado
- [ ] Guía de usuario de voz
- [ ] Documentación de API de voz
- [ ] Troubleshooting guide

**Pruebas**
- [ ] QA completo (100+ casos)
- [ ] User testing (5-10 usuarios reales)
- [ ] Performance testing (carga)
- [ ] Security audit

**Entregable**: Sistema de voz listo para producción

---

### **Fase 6 (Opcional): Mejoras Avanzadas** 🌟

#### Objetivos
- Mejoras opcionales según feedback
- Experimentación con nuevas tecnologías

#### Tareas Opcionales

**Calidad de Voz**
- [ ] Upgrade TTS a ElevenLabs (mejor calidad)
- [ ] Soporte para acentos regionales (España, México, Argentina)
- [ ] Personalización de voz (usuario elige voz preferida)

**Inteligencia**
- [ ] Memoria de conversación largo plazo
- [ ] Sugerencias proactivas ("Noté que gastaste mucho este mes...")
- [ ] Detección de emociones en voz

**Multimodalidad**
- [ ] Soporte para comandos mixtos (voz + táctil)
- [ ] Visualización de datos mientras habla
- [ ] Modo "solo voz" (sin pantalla)

**Soporte PWA**
- [ ] Instalación como app de voz
- [ ] Acceso directo por voz desde pantalla de inicio
- [ ] Notificaciones de voz

---

## 💰 Estimación de Costos

### Costos de Desarrollo

| Fase | Duración | Esfuerzo | Notas |
|------|----------|----------|-------|
| Fase 1: Fundamentos | 2 semanas | 40-60 horas | Setup inicial |
| Fase 2: Integración NLU | 2 semanas | 40-60 horas | Lógica compleja |
| Fase 3: Funcionalidades | 2 semanas | 60-80 horas | Mayor alcance |
| Fase 4: WebSocket | 1 semana | 20-30 horas | Refactoring |
| Fase 5: Producción | 1 semana | 30-40 horas | Pulido + testing |
| **TOTAL** | **8 semanas** | **190-270 horas** | 2 meses |

---

### Costos Operativos (Mensuales)

#### **Opción A: 100% Gratuito** ⭐ Recomendado

| Recurso | Servicio | Costo | Límites |
|---------|----------|-------|---------|
| **STT** | Whisper (local) | $0 | Ilimitado |
| **NLU** | Groq (gratis) | $0 | 14,400 req/día |
| **TTS** | gTTS + pyttsx3 | $0 | Ilimitado (con rate limiting suave) |
| **Hosting** | VPS básico (opcional) | $5-10 | 1 CPU, 1GB RAM |
| **TOTAL** | | **$0-10** | **~1000 usuarios/mes** |

**Limitaciones**:
- Groq: 14,400 requests/día = ~600/hora = **10 req/min promedio**
  - Con cache y optimizaciones: Soporta ~500-1000 usuarios activos/día
- gTTS: Rate limiting suave (~100 requests/min)
  - Con cache: Prácticamente ilimitado

---

#### **Opción B: Híbrida Económica** 💎 Mejor Calidad

| Recurso | Servicio | Costo | Límites |
|---------|----------|-------|---------|
| **STT** | Whisper (local) | $0 | Ilimitado |
| **NLU** | Groq (gratis) | $0 | 14,400 req/día |
| **TTS** | ElevenLabs Free + GCP | $0-5 | 10k chars (ElevenLabs) + 1M chars (GCP) |
| **Cache** | Redis Cloud (gratis) | $0 | 30MB |
| **Hosting** | VPS mejorado | $10-20 | 2 CPU, 2GB RAM |
| **TOTAL** | | **$10-25** | **~2000-5000 usuarios/mes** |

---

#### **Opción C: Profesional** 🚀 Escala Alta

| Recurso | Servicio | Costo | Límites |
|---------|----------|-------|---------|
| **STT** | Google Speech-to-Text | $10-50 | $0.006/15s después 60min gratis |
| **NLU** | Groq (gratis) | $0 | 14,400 req/día |
| **TTS** | Azure Neural TTS | $5-20 | 500k chars gratis, luego $15/1M |
| **Cache** | Redis Cloud (pago) | $7 | 250MB |
| **Hosting** | VPS potente | $20-40 | 4 CPU, 4GB RAM |
| **TOTAL** | | **$42-117** | **~10,000-50,000 usuarios/mes** |

---

### Comparativa de Opciones

| Métrica | Opción A (Gratis) | Opción B (Económica) | Opción C (Pro) |
|---------|-------------------|----------------------|----------------|
| **Costo Mensual** | $0-10 | $10-25 | $42-117 |
| **Calidad STT** | ⭐⭐⭐⭐ Excelente | ⭐⭐⭐⭐ Excelente | ⭐⭐⭐⭐⭐ Superior |
| **Calidad TTS** | ⭐⭐⭐ Buena | ⭐⭐⭐⭐⭐ Premium | ⭐⭐⭐⭐⭐ Premium |
| **Latencia** | 2-4s | 1.5-3s | 1-2s |
| **Usuarios/mes** | ~1000 | ~2000-5000 | ~10,000-50,000 |
| **Escalabilidad** | Limitada | Moderada | Alta |
| **Complejidad** | Baja | Media | Alta |

---

### 🏆 Recomendación de Ruta

```
Mes 1-3: Opción A (Gratis)
  ↓ Validar producto, obtener usuarios
  
Mes 4-6: Opción B (Económica)
  ↓ Mejorar calidad según feedback
  
Mes 7+: Opción C (Profesional)
  ↓ Escalar según demanda
```

**Inversión Total Año 1**:
- Desarrollo: ~250 horas × $0 (auto-desarrollo) = $0
- Operación: $0-10 × 12 meses = **$0-120/año**

---

## ⚠️ Riesgos y Mitigación

### Riesgos Técnicos

| Riesgo | Probabilidad | Impacto | Mitigación |
|--------|--------------|---------|------------|
| **Latencia alta de Whisper en CPU** | Media | Alto | 1. Usar modelo `small` en lugar de `medium`<br>2. Implementar GPU si disponible<br>3. Fallback a Web Speech API |
| **Rate limiting de Groq** | Baja | Medio | 1. Cache agresivo de respuestas<br>2. Respuestas template para consultas simples<br>3. Plan de pago si necesario |
| **Calidad robótica de pyttsx3** | Alta | Bajo | 1. Usar gTTS como primario<br>2. Upgrade a ElevenLabs si presupuesto permite |
| **Errores de transcripción** | Media | Medio | 1. Confirmación para acciones críticas<br>2. Corrección fuzzy de categorías/cuentas<br>3. Permitir al usuario corregir |
| **Problemas de audio del navegador** | Media | Alto | 1. Guía de permisos clara<br>2. Detección de compatibilidad<br>3. Fallback a input de texto |

---

### Riesgos de Negocio

| Riesgo | Probabilidad | Impacto | Mitigación |
|--------|--------------|---------|------------|
| **Baja adopción por usuarios** | Media | Alto | 1. Tutorial interactivo obligatorio<br>2. Ejemplos claros de comandos<br>3. Demostración en video |
| **Costos inesperados al escalar** | Baja | Medio | 1. Empezar con opción gratuita<br>2. Monitorear uso constantemente<br>3. Alerts de límites |
| **Competencia con soluciones mejores** | Media | Bajo | 1. Enfoque en nicho financiero<br>2. Personalización para usuario<br>3. Iteración rápida |

---

### Riesgos de UX

| Riesgo | Probabilidad | Impacto | Mitigación |
|--------|--------------|---------|------------|
| **Usuarios no saben qué decir** | Alta | Alto | 1. Sugerencias visuales de comandos<br>2. Botón "Ayuda por voz"<br>3. Chips de comandos rápidos |
| **Frustración por errores** | Media | Alto | 1. Mensajes de error claros<br>2. Permitir corrección fácil<br>3. Opción de deshacer |
| **Problemas de privacidad** | Baja | Alto | 1. NO guardar audio por defecto<br>2. Transparencia en uso de datos<br>3. Opción de modo offline |

---

## 📈 Métricas de Éxito

### KPIs de Producto

| Métrica | Objetivo Fase 1 | Objetivo Fase 5 | Cómo Medir |
|---------|-----------------|-----------------|------------|
| **Tasa de Adopción** | 20% usuarios prueban | 50% usuarios usan regularmente | % usuarios que hicieron ≥1 comando voz |
| **Precisión de STT** | >85% | >95% | % transcripciones correctas |
| **Tasa de Éxito de Comandos** | >70% | >90% | % comandos ejecutados correctamente |
| **Latencia Promedio** | <5s | <3s | Tiempo voz usuario → voz sistema |
| **Satisfacción de Usuario** | NPS >30 | NPS >50 | Encuestas post-uso |

---

### KPIs Técnicos

| Métrica | Objetivo | Cómo Medir |
|---------|----------|------------|
| **Uptime del Servicio de Voz** | >99% | Monitoreo continuo |
| **Errores de Procesamiento** | <5% | % requests con error |
| **Uso de Caché** | >60% | % respuestas servidas desde caché |
| **Uso de API (Groq)** | <10,000 req/día | Dashboard de Groq |

---

### KPIs de Negocio

| Métrica | Objetivo | Cómo Medir |
|---------|----------|------------|
| **Costo por Usuario Activo** | <$0.01/usuario/mes | Costos totales / MAU |
| **Retención de usuarios de voz** | >60% retención mensual | % usuarios que regresan |
| **Comandos por usuario** | >10 comandos/mes por usuario activo | Promedio de comandos |

---

## 🎯 Conclusiones y Próximos Pasos

### Resumen de la Propuesta

Esta especificación técnica detalla un **sistema completo de chat de voz bidireccional** que permite a los usuarios de la aplicación de gestión financiera controlar todas las funcionalidades mediante comandos de voz naturales, manteniendo un **costo operativo de $0-10/mes**.

#### **Pilares de la Solución**

1. **🎙️ Speech-to-Text**: OpenAI Whisper (local, gratuito, precisión >90%)
2. **🧠 NLU**: Groq Llama 3.3 (ya integrado, gratuito, excelente comprensión)
3. **🔊 Text-to-Speech**: gTTS + pyttsx3 (dual, gratuito, calidad aceptable)
4. **⚡ Comunicación**: WebSocket (Flask-SocketIO, tiempo real)
5. **🎯 Experiencia**: Conversacional natural, no comandos rígidos

#### **Beneficios Clave**

✅ **100% de funciones accesibles por voz** (12 intenciones mapeadas)  
✅ **Costo operativo mínimo** ($0-10/mes para 1000 usuarios)  
✅ **Latencia aceptable** (2-4s inicialmente, optimizable a <3s)  
✅ **Escalable** (arquitectura preparada para upgrade)  
✅ **Accesible** (beneficia a usuarios con discapacidades)

---

### Próximos Pasos Inmediatos

#### **1. Aprobación y Priorización** (Día 1)
- [ ] Revisar esta especificación con stakeholders
- [ ] Decidir qué fases implementar (mínimo Fase 1-3 recomendado)
- [ ] Asignar recursos y timeline

#### **2. Setup del Entorno** (Día 2-3)
```bash
# Instalar dependencias de voz
pip install openai-whisper torch gTTS pyttsx3 pydub flask-socketio

# Descargar modelo Whisper
python -c "import whisper; whisper.load_model('medium')"

# Verificar instalaciones
python -c "from gtts import gTTS; import pyttsx3; print('TTS OK')"
```

#### **3. Proof of Concept** (Día 4-7)
- [ ] Implementar endpoint `/api/voice/test`
- [ ] Frontend minimalista de captura de audio
- [ ] Conectar Whisper → Groq → gTTS
- [ ] Probar flujo completo voz a voz

#### **4. Primera Demo** (Día 8)
- [ ] Grabar video de demostración
- [ ] Mostrar 3 comandos funcionando:
  1. "¿Cuál es mi balance?"
  2. "Gasté 50 en comida"
  3. "¿Cuánto gasté este mes?"
- [ ] Obtener feedback inicial

---

### Recursos Adicionales

#### **Documentación Técnica**
- [OpenAI Whisper GitHub](https://github.com/openai/whisper)
- [gTTS Documentation](https://gtts.readthedocs.io/)
- [Flask-SocketIO Docs](https://flask-socketio.readthedocs.io/)
- [Groq API Docs](https://console.groq.com/docs)

#### **Tutoriales Recomendados**
- [Building Voice Interfaces with Whisper](https://platform.openai.com/docs/guides/speech-to-text)
- [Real-time Communication with WebSocket](https://socket.io/docs/v4/)
- [Optimizing Whisper Performance](https://github.com/openai/whisper/discussions/categories/performance)

#### **Herramientas de Testing**
- **Audacity**: Edición de audio para pruebas
- **Postman/Insomnia**: Testing de API de voz
- **Socket.IO Client**: Testing de WebSocket

---

### Contacto y Soporte

Para preguntas o aclaraciones sobre esta especificación:

- **Documentación Principal**: `docs/VOICE_CHAT_REDESIGN_SPEC.md`
- **Issues/Bugs**: Crear issue en repositorio
- **Mejoras**: Pull requests bienvenidos

---

## 📄 Licencia

Este documento es parte del proyecto OrdenC - Gestor Financiero.  
Sujeto a la misma licencia del proyecto principal.

---

**Versión**: 1.0  
**Fecha**: 2 de marzo de 2026  
**Autor**: Especificación Técnica Generada por AI Assistant  
**Última Actualización**: 2 de marzo de 2026

---

## 🎉 ¡Gracias!

Este rediseño transformará la aplicación en una herramienta verdaderamente **hands-free** y **accesible**, permitiendo a los usuarios gestionar sus finanzas de forma natural mediante voz.

**¡Hagamos que hablar con tus finanzas sea tan fácil como hablar con un amigo!** 🎙️💰
