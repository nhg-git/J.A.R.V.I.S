"""
audio_manager.py

Manages microphone recording state for server-side audio capture.
Note: In most JARVIS deployments the browser captures audio and
sends it over WebSocket. This module is for optional server-side
recording (e.g. if running JARVIS on the same machine without a browser).
"""
from app.services.logger import get_logger

logger = get_logger("voice.audio")

# Browser-captured audio (base64 → WebSocket) is the primary path.
# Server-side mic recording is a secondary, optional feature.


def record_from_mic(duration_seconds: float = 5.0, sample_rate: int = 16000) -> bytes:
    """
    Record audio from the system microphone.
    Returns raw WAV bytes.
    """
    try:
        import sounddevice as sd
        import soundfile as sf
        import numpy as np
        import io

        logger.info(f"Recording for {duration_seconds}s...")
        audio = sd.rec(
            int(duration_seconds * sample_rate),
            samplerate=sample_rate,
            channels=1,
            dtype="float32",
        )
        sd.wait()

        buf = io.BytesIO()
        sf.write(buf, audio, sample_rate, format="WAV", subtype="PCM_16")
        return buf.getvalue()

    except Exception as e:
        logger.error(f"Mic recording error: {e}")
        return b""
