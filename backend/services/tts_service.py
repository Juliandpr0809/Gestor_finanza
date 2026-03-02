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
        try:
            self.offline_engine = pyttsx3.init()
            self.offline_engine.setProperty('rate', 150)  # Velocidad
            self.offline_engine.setProperty('volume', 0.9)
            self.has_offline = True
        except Exception as e:
            print(f"[TTS WARNING] pyttsx3 init failed: {e}")
            self.has_offline = False
        
        print("[TTS SERVICE] Initialized with gTTS (primary) + pyttsx3 (fallback) ✅")
    
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
        # Verificar caché primero
        if use_cache:
            cached_file = self._get_cached_audio(text)
            if cached_file:
                print(f"[TTS SERVICE] ✅ Using cached audio")
                return cached_file
        
        # Intentar gTTS con reintentos
        gtts_error = None
        for attempt in range(2):  # 2 intentos
            try:
                audio_path = self._synthesize_gtts(text, language)
                print(f"[TTS SERVICE] ✅ Audio generated with gTTS (attempt {attempt+1})")
                return audio_path
            except Exception as e:
                gtts_error = str(e)
                print(f"[TTS SERVICE] gTTS failed (attempt {attempt+1}): {gtts_error}")
                if attempt == 0:
                    import time
                    time.sleep(1)  # Esperar antes de reintentar
                continue
        
        # Si gTTS falló, usar fallback offline
        print(f"[TTS SERVICE] ⚠️ gTTS unavailable. Usando pyttsx3 offline...")
        if self.has_offline:
            try:
                audio_path = self._synthesize_offline(text)
                print(f"[TTS SERVICE] ✅ Audio generated with pyttsx3 (offline)")
                return audio_path
            except Exception as offline_error:
                print(f"[TTS SERVICE] ❌ pyttsx3 also failed: {offline_error}")
                raise Exception(f"TTS failed: gTTS={gtts_error}, pyttsx3={offline_error}")
        else:
            raise Exception(f"No TTS available. gTTS failed: {gtts_error}, pyttsx3 not available")
    
    
    def _synthesize_gtts(self, text, language):
        """Síntesis con Google TTS (online)"""
        file_path = self.cache_dir / f"{self._text_hash(text)}.mp3"
        
        # Determinar TLD según idioma
        tld = 'com.mx' if language == 'es' else 'com'
        
        tts = gTTS(text=text, lang=language, slow=False, tld=tld)
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

# Singleton
tts_service = TTSService()
