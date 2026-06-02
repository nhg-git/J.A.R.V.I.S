import base64
import os
import tempfile
from typing import Optional

from app.services.settings import settings
from app.services.logger import get_logger

logger = get_logger("voice.stt")

_model = None  # Lazy-loaded


def get_whisper_model():
    """Load the Whisper model once and cache it."""
    global _model
    if _model is None:
        try:
            from faster_whisper import WhisperModel

            logger.info(
                f"Loading Whisper model: {settings.WHISPER_MODEL_SIZE} "
                "(this may take a moment first time)"
            )
            _model = WhisperModel(
                settings.WHISPER_MODEL_SIZE,
                device="cpu",
                compute_type="int8",      # Fast on CPU
            )
            logger.info("Whisper model loaded ✓")
        except ImportError:
            logger.error("faster-whisper not installed. Run: pip install faster-whisper")
            raise
    return _model


def transcribe_audio_file(audio_path: str) -> Optional[str]:
    """Transcribe an audio file and return the text."""
    try:
        model = get_whisper_model()
        segments, info = model.transcribe(
            audio_path,
            beam_size=5,
            language="en",
            vad_filter=True,              # Filter out silence
            vad_parameters={"min_silence_duration_ms": 500},
        )

        text = " ".join(seg.text.strip() for seg in segments).strip()
        logger.info(f"Transcribed: '{text[:80]}' | lang={info.language}")
        return text if text else None

    except Exception as e:
        logger.error(f"Transcription error: {e}")
        return None


def transcribe_base64_audio(b64_audio: str) -> Optional[str]:
    """
    Transcribe base64-encoded audio (webm/wav/mp3).
    Used when receiving audio from the browser via WebSocket.
    """
    try:
        audio_bytes = base64.b64decode(b64_audio)

        # Write to a temp file (Whisper needs a file path)
        with tempfile.NamedTemporaryFile(suffix=".webm", delete=False) as f:
            f.write(audio_bytes)
            tmp_path = f.name

        try:
            return transcribe_audio_file(tmp_path)
        finally:
            os.unlink(tmp_path)

    except Exception as e:
        logger.error(f"Base64 audio transcription error: {e}")
        return None
