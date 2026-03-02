"""
Servicio de Speech-to-Text usando Deepgram (Cloud, Gratis)
"""
import os
import requests

class VoiceService:
    def __init__(self):
        # API Key desde .env
        self.api_key = os.environ.get('DEEPGRAM_API_KEY')
        if not self.api_key:
            print("[WARNING] DEEPGRAM_API_KEY no encontrada en .env")
            self.enabled = False
            self.init_error = "DEEPGRAM_API_KEY no configurada"
        else:
            self.enabled = True
            self.init_error = None
            print("[VOICE SERVICE] Deepgram STT initialized ✅")
    
    def transcribe(self, audio_input, language='es'):
        """
        Transcribe audio usando Deepgram
        
        Args:
            audio_input: Ruta al archivo de audio (str) o datos binarios (bytes)
            language: es, en, etc.
        
        Returns:
            str: Texto transcrito
        """
        if not self.enabled:
            raise Exception(f"Deepgram no disponible: {self.init_error}")
        
        try:
            # Leer datos de audio
            if isinstance(audio_input, str):
                # Es una ruta de archivo
                with open(audio_input, 'rb') as audio:
                    buffer_data = audio.read()
            elif isinstance(audio_input, bytes):
                # Es data binaria directa
                buffer_data = audio_input
            else:
                raise Exception("audio_input debe ser str (ruta) o bytes (data)")

            # Detectar tipo de audio
            content_type = self._detect_audio_type(buffer_data)
            
            print(f"[DEEPGRAM] Audio size: {len(buffer_data)} bytes, type: {content_type}")

            # API HTTP directa de Deepgram (evita incompatibilidades del SDK)
            url = (
                f"https://api.deepgram.com/v1/listen"
                f"?model=nova-2&language={language}&punctuate=true&smart_format=true"
            )
            headers = {
                "Authorization": f"Token {self.api_key}",
                "Content-Type": content_type
            }

            print(f"[DEEPGRAM] Sending request to {url}")
            response = requests.post(url, headers=headers, data=buffer_data, timeout=45)
            
            if response.status_code != 200:
                error_msg = response.text
                print(f"[DEEPGRAM] ❌ HTTP {response.status_code}: {error_msg}")
                raise Exception(f"Deepgram API error {response.status_code}: {error_msg}")
                
            data = response.json()
            print(f"[DEEPGRAM] Raw response: {data}")

            # Extraer texto
            transcript = (
                data.get('results', {})
                .get('channels', [{}])[0]
                .get('alternatives', [{}])[0]
                .get('transcript', '')
            )
            
            # Si no hay transcripción, verificar si hay al menos un resultado
            if not transcript:
                # Checkear si Deepgram detectó audio
                try:
                    results = data.get('results', {})
                    if not results:
                        raise Exception("Deepgram no devolvió resultados: audio muy corto o sin contenido")
                    
                    channels = results.get('channels', [])
                    if not channels:
                        raise Exception("Deepgram sin canales de audio: el archivo puede estar corrupto")
                    
                    alternatives = channels[0].get('alternatives', [])
                    if not alternatives:
                        raise Exception("Deepgram sin alternativas: lenguaje no detectado o silencio")
                    
                    # Si hay alternativas pero transcript vacío
                    confidence = alternatives[0].get('confidence', 0)
                    if confidence < 0.5:
                        raise Exception(f"Audio poco confiable (confidence: {confidence:.2f}): silencio o ruido de fondo")
                    
                    raise Exception("Deepgram no devolvió transcripción válida (audio muy corto)")
                except Exception as detail_error:
                    raise detail_error
            
            print(f"[DEEPGRAM] ✅ Transcribed: {transcript}")
            return transcript.strip()
            
        except Exception as e:
            print(f"[DEEPGRAM] ❌ Error: {e}")
            import traceback
            traceback.print_exc()
            raise
    
    def _detect_audio_type(self, audio_data):
        """
        Detecta el tipo MIME del audio según su header mágico
        """
        if len(audio_data) < 4:
            return "audio/wav"  # Por defecto
        
        # Verificar headers mágicos
        if audio_data[:4] == b'RIFF':
            return "audio/wav"
        elif audio_data[:4] == b'\xff\xfb' or audio_data[:2] == b'\xff\xfa':
            return "audio/mpeg"
        elif audio_data[:4] == b'OggS':
            return "audio/ogg"
        elif audio_data[:4] == b'\x1a\x45\xdf\xa3':  # EBML para WebM
            return "audio/webm"
        elif audio_data[:3] == b'ID3' or audio_data[:4] == b'\xff\xfb':
            return "audio/mpeg"
        
        # Por defecto, asumir WAV si no hay header identificable
        return "audio/wav"

# Singleton
voice_service = VoiceService()
