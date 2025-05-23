"""
Text-to-Speech engine for the AI Accessibility Reader.
Uses multiple TTS engines with fallbacks for maximum compatibility.
"""

import os
import tempfile
import logging
import platform
import subprocess
import sys
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global TTS engine instance
current_tts_engine = None
current_engine_type = None

class TTSEngine:
    """Base class for TTS engines"""
    def __init__(self):
        self.initialized = False
    
    def initialize(self):
        raise NotImplementedError
    
    def text_to_speech(self, text, output_path):
        raise NotImplementedError

class GTTSEngine(TTSEngine):
    """Google Text-to-Speech (requires internet)"""
    def __init__(self):
        super().__init__()
        self.gtts = None
    
    def initialize(self):
        try:
            from gtts import gTTS
            import requests
            
            # Test internet connection
            requests.get("https://www.google.com", timeout=5)
            
            # Test gTTS with a simple phrase
            test_tts = gTTS(text="test", lang='en')
            with tempfile.NamedTemporaryFile(suffix='.mp3', delete=True) as temp_file:
                test_tts.save(temp_file.name)
                if os.path.exists(temp_file.name) and os.path.getsize(temp_file.name) > 0:
                    self.initialized = True
                    logger.info("gTTS engine initialized successfully")
                    return True
        except Exception as e:
            logger.warning(f"gTTS initialization failed: {str(e)}")
            return False
        return False
    
    def text_to_speech(self, text, output_path):
        from gtts import gTTS
        from pydub import AudioSegment
        
        # Split text into chunks (gTTS has character limits)
        chunks = self._split_text(text, max_chars=5000)
        audio_segments = []
        
        with tempfile.TemporaryDirectory() as temp_dir:
            for i, chunk in enumerate(chunks):
                temp_path = os.path.join(temp_dir, f"chunk_{i}.mp3")
                tts = gTTS(text=chunk, lang='en', slow=False)
                tts.save(temp_path)
                audio_segments.append(AudioSegment.from_mp3(temp_path))
            
            # Combine segments
            final_audio = sum(audio_segments)
            final_audio.export(output_path, format="mp3", bitrate="192k")
    
    def _split_text(self, text, max_chars=5000):
        if len(text) <= max_chars:
            return [text]
        
        chunks = []
        sentences = text.replace('\n', ' ').split('.')
        current_chunk = ""
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
            sentence += '.'
            
            if len(current_chunk) + len(sentence) > max_chars:
                if current_chunk.strip():
                    chunks.append(current_chunk.strip())
                current_chunk = sentence
            else:
                current_chunk += " " + sentence if current_chunk else sentence
        
        if current_chunk.strip():
            chunks.append(current_chunk.strip())
        
        return chunks or [text[:max_chars]]

class PytttsxEngine(TTSEngine):
    """Offline TTS using pyttsx3 (system TTS)"""
    def __init__(self):
        super().__init__()
        self.engine = None
    
    def initialize(self):
        try:
            import pyttsx3
            
            self.engine = pyttsx3.init()
            
            # Configure engine
            voices = self.engine.getProperty('voices')
            if voices:
                # Try to find an English voice
                english_voice = None
                for voice in voices:
                    if 'en' in voice.id.lower() or 'english' in voice.name.lower():
                        english_voice = voice
                        break
                
                if english_voice:
                    self.engine.setProperty('voice', english_voice.id)
                else:
                    self.engine.setProperty('voice', voices[0].id)
            
            # Set speech rate and volume
            self.engine.setProperty('rate', 200)  # Speed of speech
            self.engine.setProperty('volume', 0.9)  # Volume level (0.0 to 1.0)
            
            # Test the engine
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=True) as temp_file:
                self.engine.save_to_file("test", temp_file.name)
                self.engine.runAndWait()
                
                if os.path.exists(temp_file.name):
                    self.initialized = True
                    logger.info("pyttsx3 engine initialized successfully")
                    return True
                    
        except Exception as e:
            logger.warning(f"pyttsx3 initialization failed: {str(e)}")
            return False
        return False
    
    def text_to_speech(self, text, output_path):
        import pyttsx3
        import shutil
        
        # For Windows without ffmpeg, save directly as WAV and convert to MP3 manually
        try:
            from pydub import AudioSegment
            has_pydub = True
        except:
            has_pydub = False
        
        # Split text into manageable chunks
        chunks = self._split_text(text, max_chars=1000)
        
        with tempfile.TemporaryDirectory() as temp_dir:
            wav_files = []
            
            for i, chunk in enumerate(chunks):
                wav_path = os.path.join(temp_dir, f"chunk_{i}.wav")
                
                # Create a new engine instance for each chunk
                engine = pyttsx3.init()
                
                # Configure engine
                voices = engine.getProperty('voices')
                if voices:
                    english_voice = None
                    for voice in voices:
                        if 'en' in voice.id.lower() or 'english' in voice.name.lower():
                            english_voice = voice
                            break
                    if english_voice:
                        engine.setProperty('voice', english_voice.id)
                    else:
                        engine.setProperty('voice', voices[0].id)
                
                engine.setProperty('rate', 200)
                engine.setProperty('volume', 0.9)
                
                # Generate audio
                engine.save_to_file(chunk, wav_path)
                engine.runAndWait()
                engine.stop()
                
                if os.path.exists(wav_path) and os.path.getsize(wav_path) > 0:
                    wav_files.append(wav_path)
            
            if not wav_files:
                raise RuntimeError("No audio segments were generated")
            
            # Try to combine with pydub if available, otherwise just copy the first file
            if has_pydub and len(wav_files) > 1:
                try:
                    # Try to combine segments
                    audio_segments = [AudioSegment.from_wav(f) for f in wav_files]
                    final_audio = sum(audio_segments)
                    
                    # Try to export as MP3, fallback to WAV
                    try:
                        final_audio.export(output_path, format="mp3", bitrate="192k")
                    except:
                        # If MP3 export fails, save as WAV
                        wav_output = output_path.replace('.mp3', '.wav')
                        final_audio.export(wav_output, format="wav")
                        # Rename to requested path
                        if wav_output != output_path:
                            shutil.move(wav_output, output_path)
                except Exception as e:
                    logger.warning(f"Pydub processing failed: {e}, falling back to single file")
                    # Just copy the first WAV file
                    shutil.copy2(wav_files[0], output_path)
            else:
                # Just copy the first (or only) WAV file
                shutil.copy2(wav_files[0], output_path)
    
    def _split_text(self, text, max_chars=1000):
        if len(text) <= max_chars:
            return [text]
        
        chunks = []
        sentences = text.replace('\n', ' ').split('.')
        current_chunk = ""
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
            sentence += '.'
            
            if len(current_chunk) + len(sentence) > max_chars:
                if current_chunk.strip():
                    chunks.append(current_chunk.strip())
                current_chunk = sentence
            else:
                current_chunk += " " + sentence if current_chunk else sentence
        
        if current_chunk.strip():
            chunks.append(current_chunk.strip())
        
        return chunks or [text[:max_chars]]

class CoquiTTSEngine(TTSEngine):
    """Coqui TTS (your original engine)"""
    def __init__(self):
        super().__init__()
        self.tts_model = None
    
    def initialize(self):
        try:
            from TTS.api import TTS
            import requests
            
            # Check internet connection
            requests.get("https://www.google.com", timeout=5)
            
            # Create cache directory
            cache_dir = os.path.join(os.getcwd(), "tts_cache")
            os.makedirs(cache_dir, exist_ok=True)
            
            # Try different models
            models = [
                "tts_models/en/ljspeech/tacotron2-DDC",
                "tts_models/en/ljspeech/glow-tts",
                "tts_models/en/vctk/vits"
            ]
            
            for model_name in models:
                try:
                    logger.info(f"Trying Coqui model: {model_name}")
                    self.tts_model = TTS(model_name=model_name, progress_bar=True, cache_dir=cache_dir)
                    
                    # Test the model
                    with tempfile.NamedTemporaryFile(suffix='.wav', delete=True) as temp_file:
                        self.tts_model.tts_to_file(text="Hello test", file_path=temp_file.name)
                        if os.path.exists(temp_file.name) and os.path.getsize(temp_file.name) > 0:
                            self.initialized = True
                            logger.info(f"Coqui TTS initialized with model: {model_name}")
                            return True
                except Exception as e:
                    logger.warning(f"Coqui model {model_name} failed: {str(e)}")
                    continue
                    
        except Exception as e:
            logger.warning(f"Coqui TTS initialization failed: {str(e)}")
            return False
        return False
    
    def text_to_speech(self, text, output_path):
        from pydub import AudioSegment
        
        chunks = self._split_text(text, max_chars=500)
        audio_segments = []
        
        with tempfile.TemporaryDirectory() as temp_dir:
            for i, chunk in enumerate(chunks):
                wav_path = os.path.join(temp_dir, f"chunk_{i}.wav")
                self.tts_model.tts_to_file(text=chunk, file_path=wav_path)
                
                if os.path.exists(wav_path) and os.path.getsize(wav_path) > 0:
                    audio_segments.append(AudioSegment.from_wav(wav_path))
            
            final_audio = sum(audio_segments)
            final_audio.export(output_path, format="mp3", bitrate="192k")
    
    def _split_text(self, text, max_chars=500):
        if len(text) <= max_chars:
            return [text]
        
        chunks = []
        sentences = text.replace('\n', ' ').split('.')
        current_chunk = ""
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
            sentence += '.'
            
            if len(current_chunk) + len(sentence) > max_chars:
                if current_chunk.strip():
                    chunks.append(current_chunk.strip())
                current_chunk = sentence
            else:
                current_chunk += " " + sentence if current_chunk else sentence
        
        if current_chunk.strip():
            chunks.append(current_chunk.strip())
        
        return chunks or [text[:max_chars]]

def initialize_tts():
    """Initialize TTS with multiple fallback engines"""
    global current_tts_engine, current_engine_type
    
    # List of engines to try in order of preference
    engines_to_try = [
        ("pyttsx3", PytttsxEngine),
        ("gTTS", GTTSEngine),
        ("Coqui", CoquiTTSEngine),
    ]
    
    for engine_name, engine_class in engines_to_try:
        logger.info(f"Trying {engine_name} TTS engine...")
        try:
            engine = engine_class()
            if engine.initialize():
                current_tts_engine = engine
                current_engine_type = engine_name
                logger.info(f"Successfully initialized {engine_name} TTS engine")
                return
        except Exception as e:
            logger.warning(f"{engine_name} engine failed: {str(e)}")
            continue
    
    raise RuntimeError("All TTS engines failed to initialize. Please check your system setup.")

def text_to_speech(text, output_path):
    """Convert text to speech using the initialized engine"""
    global current_tts_engine
    
    if not text or not text.strip():
        raise ValueError("No text provided for TTS conversion")
    
    if current_tts_engine is None:
        logger.info("Initializing TTS engine...")
        initialize_tts()
    
    if current_tts_engine is None:
        raise RuntimeError("No TTS engine available")
    
    try:
        logger.info(f"Converting text to speech using {current_engine_type} engine...")
        logger.info(f"Text length: {len(text)} characters")
        
        current_tts_engine.text_to_speech(text, output_path)
        
        # Verify output file
        if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
            logger.info(f"Audio saved successfully: {output_path} ({os.path.getsize(output_path)} bytes)")
        else:
            raise RuntimeError("Failed to create output audio file")
            
    except Exception as e:
        logger.exception(f"TTS conversion failed with {current_engine_type} engine")
        raise RuntimeError(f"Failed to convert text to speech: {str(e)}")

def get_current_engine():
    """Get information about the current TTS engine"""
    global current_engine_type, current_tts_engine
    return {
        "engine": current_engine_type,
        "initialized": current_tts_engine is not None and current_tts_engine.initialized
    }

def get_available_engines():
    """Get list of potentially available engines"""
    available = []
    
    # Check pyttsx3
    try:
        import pyttsx3
        available.append("pyttsx3 (offline)")
    except ImportError:
        pass
    
    # Check gTTS
    try:
        import gtts
        import requests
        requests.get("https://www.google.com", timeout=5)
        available.append("gTTS (online)")
    except:
        pass
    
    # Check Coqui TTS
    try:
        import TTS
        available.append("Coqui TTS (offline)")
    except ImportError:
        pass
    
    return available

# Backward compatibility functions
tts_model = None

def split_text_into_chunks(text, max_chars=500):
    """Backward compatibility function"""
    if not text or not text.strip():
        return [""]
    
    chunks = []
    sentences = text.replace('\n', ' ').split('.')
    current_chunk = ""
    
    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue
        sentence += '.'
        
        if len(current_chunk) + len(sentence) > max_chars:
            if current_chunk.strip():
                chunks.append(current_chunk.strip())
            current_chunk = sentence
        else:
            current_chunk += " " + sentence if current_chunk else sentence
    
    if current_chunk.strip():
        chunks.append(current_chunk.strip())
    
    return chunks or [text]

if __name__ == "__main__":
    # Test the TTS engine
    print("Available engines:", get_available_engines())
    
    test_text = "Hello, this is a test of the text to speech engine. It should work with multiple fallback engines."
    output_file = "test_output.mp3"
    
    try:
        text_to_speech(test_text, output_file)
        print(f"Test successful! Audio saved to {output_file}")
        print(f"Using engine: {get_current_engine()}")
    except Exception as e:
        print(f"Test failed: {str(e)}")
        print("Available engines:", get_available_engines())