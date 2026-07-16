"""
Text-to-Speech (TTS) service using Piper.
- FastAPI friendly
- Lazy-loaded models (doesn't load on import)
- Supports Arabic/English with automatic language detection
- Safe temp-file handling
"""

from __future__ import annotations

import os
import io
import tempfile
import wave
from dataclasses import dataclass
from typing import Optional, Literal, Iterator
from pathlib import Path

try:
    from piper.voice import PiperVoice
    from piper.config import PiperConfig
    PIPER_AVAILABLE = True
except ImportError:
    PIPER_AVAILABLE = False
    print("⚠️ Warning: piper-tts not available. TTS features will be disabled.")


Language = Literal["en", "ar", "auto"]


@dataclass
class TTSConfig:
    """Configuration for TTS service"""
    model_en: str = "en_US-lessac-medium"
    model_ar: str = "ar_JO-kareem-medium"
    models_dir: str = "./models/piper"
    sample_rate: int = 22050
    enabled: bool = True


@dataclass
class TTSResult:
    """Result from TTS synthesis"""
    audio_data: bytes
    sample_rate: int
    language: str
    duration: Optional[float] = None


class TextToSpeechService:
    """
    Lazy TTS service wrapper around Piper.
    Supports English and Arabic with automatic language detection.
    """

    def __init__(self, config: Optional[TTSConfig] = None):
        self.config = config or TTSConfig()
        self._voice_en: Optional[PiperVoice] = None
        self._voice_ar: Optional[PiperVoice] = None
        self._models_dir = Path(self.config.models_dir)
        self._models_dir.mkdir(parents=True, exist_ok=True)

    def _is_arabic(self, text: str) -> bool:
        """Check if text contains Arabic characters"""
        if not text:
            return False
        # Check for Arabic Unicode range
        arabic_chars = sum(1 for char in text if '\u0600' <= char <= '\u06FF')
        # If more than 20% of characters are Arabic, consider it Arabic
        return arabic_chars > len(text) * 0.2

    def _clean_text(self, text: str) -> str:
        """Remove markdown formatting for better TTS"""
        import re
        # Remove headings (e.g. ## Title)
        text = re.sub(r'^#+\s+', '', text, flags=re.MULTILINE)
        # Remove bold/italic (**text**, *text*)
        text = re.sub(r'\*\*|__', '', text)
        text = re.sub(r'\*|_', '', text)
        # Remove links [text](url) -> text
        text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)
        # Remove code blocks (`code`)
        text = re.sub(r'`', '', text)
        
        # Simplify time formats for TTS: 4:00 PM -> 4 PM
        # Matches digit(s):00 followed optionally by AM/PM
        text = re.sub(r'(\d{1,2}):00\s*(?=[APap][Mm]|\b)', r'\1 ', text)
        
        return text.strip()

    def _detect_language(self, text: str) -> str:
        """Detect language from text (en or ar)"""
        return "ar" if self._is_arabic(text) else "en"

    def _get_model_path(self, language: str) -> tuple[Path, Path]:
        """
        Get model and config paths for a language.
        Returns (model_path, config_path)
        """
        if language == "en":
            model_name = self.config.model_en
        elif language == "ar":
            model_name = self.config.model_ar
        else:
            raise ValueError(f"Unsupported language: {language}")

        # Model files should be in models_dir/model_name/
        model_dir = self._models_dir / model_name
        
        # Piper models use lowercase with hyphens (e.g., en-us-lessac-medium.onnx)
        # Convert underscore to hyphen and lowercase
        model_filename = model_name.replace("_", "-").lower()
        model_file = model_dir / f"{model_filename}.onnx"
        config_file = model_dir / f"{model_filename}.onnx.json"

        return model_file, config_file

    def _load_voice(self, language: str) -> PiperVoice:
        """
        Load Piper voice model for specified language.
        """
        if not PIPER_AVAILABLE:
            raise RuntimeError("Piper TTS is not installed. Please install piper-tts.")

        if language == "en":
            if self._voice_en is not None:
                return self._voice_en
        elif language == "ar":
            if self._voice_ar is not None:
                return self._voice_ar
        else:
            raise ValueError(f"Unsupported language: {language}")

        print(f"🔊 Loading Piper TTS model for {language}...")

        try:
            model_path, config_path = self._get_model_path(language)

            if not model_path.exists():
                raise FileNotFoundError(
                    f"Model file not found: {model_path}\n"
                    f"Please download the model from: https://github.com/rhasspy/piper/releases\n"
                    f"Expected location: {model_path}"
                )

            if not config_path.exists():
                raise FileNotFoundError(
                    f"Config file not found: {config_path}\n"
                    f"Please download the config file along with the model."
                )

            # Load the voice
            voice = PiperVoice.load(
                model_path=str(model_path),
                config_path=str(config_path),
                use_cuda=False  # Use CPU for now
            )

            # Cache the loaded voice
            if language == "en":
                self._voice_en = voice
            else:
                self._voice_ar = voice

            print(f"✅ Loaded {language} model successfully")
            return voice

        except Exception as e:
            print(f"❌ Error loading Piper model for {language}: {e}")
            raise RuntimeError(f"Failed to load TTS model for {language}: {e}")

    def synthesize_text(
        self,
        text: str,
        language: Language = "auto",
    ) -> TTSResult:
        """
        Synthesize speech from text.
        
        Args:
            text: Text to synthesize
            language: Language code ("en", "ar", or "auto" for detection)
        
        Returns:
            TTSResult with audio data and metadata
        """
        if not self.config.enabled:
            raise RuntimeError("TTS is disabled in configuration")

        if not text or not text.strip():
            raise ValueError("Text cannot be empty")

        # Clean text (remove markdown)
        text = self._clean_text(text)

        # Detect language if auto
        if language == "auto":
            language = self._detect_language(text)

        # Load appropriate voice
        voice = self._load_voice(language)

        # Synthesize audio - collect all audio chunks
        audio_bytes = bytearray()
        for audio_chunk in voice.synthesize(text):
            audio_bytes.extend(audio_chunk.audio_int16_bytes)

        return TTSResult(
            audio_data=bytes(audio_bytes),
            sample_rate=voice.config.sample_rate,
            language=language,
        )

    def synthesize_to_file(
        self,
        text: str,
        output_path: str,
        language: Language = "auto",
    ) -> TTSResult:
        """
        Synthesize speech and save to WAV file.
        
        Args:
            text: Text to synthesize
            output_path: Path to save WAV file
            language: Language code ("en", "ar", or "auto")
        
        Returns:
            TTSResult with audio data and metadata
        """
        result = self.synthesize_text(text, language)

        # Write WAV file
        with wave.open(output_path, 'wb') as wav_file:
            wav_file.setnchannels(1)  # Mono
            wav_file.setsampwidth(2)  # 16-bit
            wav_file.setframerate(result.sample_rate)
            wav_file.writeframes(result.audio_data)

        return result

    def synthesize_to_temp_file(
        self,
        text: str,
        language: Language = "auto",
        suffix: str = ".wav",
    ) -> tuple[str, TTSResult]:
        """
        Synthesize speech and save to temporary file.
        
        Args:
            text: Text to synthesize
            language: Language code ("en", "ar", or "auto")
            suffix: File suffix (default: .wav)
        
        Returns:
            Tuple of (temp_file_path, TTSResult)
        """
        result = self.synthesize_text(text, language)

        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            temp_path = tmp.name

        # Write WAV file
        with wave.open(temp_path, 'wb') as wav_file:
            wav_file.setnchannels(1)  # Mono
            wav_file.setsampwidth(2)  # 16-bit
            wav_file.setframerate(result.sample_rate)
            wav_file.writeframes(result.audio_data)

        return temp_path, result


# ---- Dependency-friendly singleton factory (FastAPI use) ----

_tts_singleton: Optional[TextToSpeechService] = None


def get_tts_service() -> TextToSpeechService:
    """
    Get singleton TTS service instance.
    Use this as a FastAPI dependency:
        tts = Depends(get_tts_service)
    """
    global _tts_singleton
    if _tts_singleton is None:
        from twuaqirag.core.config import config
        
        _tts_singleton = TextToSpeechService(
            TTSConfig(
                model_en=os.getenv("TTS_MODEL_EN", "en_US-lessac-medium"),
                model_ar=os.getenv("TTS_MODEL_AR", "ar_JO-kareem-medium"),
                models_dir=os.getenv("TTS_MODELS_DIR", str(config.MODELS_DIR / "piper")),
                sample_rate=int(os.getenv("TTS_SAMPLE_RATE", "22050")),
                enabled=os.getenv("TTS_ENABLED", "true").lower() == "true",
            )
        )
    return _tts_singleton


