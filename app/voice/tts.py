import asyncio
import base64
import re
from typing import Optional

from app.services.settings import settings
from app.services.logger import get_logger

logger = get_logger("voice.tts")


def _clean_text_for_tts(text: str) -> str:
    """Strip markdown and code blocks before speaking."""
    # Remove code blocks
    text = re.sub(r"```[\s\S]*?```", "[code block]", text)
    text = re.sub(r"`[^`]*`", "", text)
    # Remove markdown headers
    text = re.sub(r"^#{1,6}\s+", "", text, flags=re.MULTILINE)
    # Remove bold/italic markers
    text = re.sub(r"[*_]{1,3}([^*_]+)[*_]{1,3}", r"\1", text)
    # Remove URLs
    text = re.sub(r"https?://\S+", "", text)
    # Remove [n] citation markers
    text = re.sub(r"\[\d+\]", "", text)
    # Collapse whitespace
    text = re.sub(r"\s+", " ", text).strip()
    return text


async def synthesise_speech(text: str, voice: Optional[str] = None) -> Optional[bytes]:
    """
    Convert text to MP3 audio bytes using Edge TTS (free, no API key).
    Returns None if TTS is disabled or an error occurs.
    """
    if not settings.ENABLE_TTS:
        return None

    try:
        import edge_tts

        voice = voice or settings.TTS_VOICE
        clean = _clean_text_for_tts(text)

        if not clean or len(clean) < 3:
            return None

        # Truncate very long responses for voice
        if len(clean) > 1000:
            clean = clean[:1000] + "..."

        communicate = edge_tts.Communicate(clean, voice)
        audio_data = b""

        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_data += chunk["data"]

        logger.debug(f"TTS generated: {len(audio_data)} bytes | voice={voice}")
        return audio_data

    except ImportError:
        logger.error("edge-tts not installed. Run: pip install edge-tts")
        return None
    except Exception as e:
        logger.error(f"TTS synthesis error: {e}")
        return None


async def text_to_base64_audio(text: str) -> Optional[str]:
    """Synthesise speech and return as base64 string for WebSocket transport."""
    audio_bytes = await synthesise_speech(text)
    if audio_bytes:
        return base64.b64encode(audio_bytes).decode("utf-8")
    return None


async def list_available_voices() -> list[dict]:
    """Return a list of available Edge TTS voices."""
    try:
        import edge_tts
        voices = await edge_tts.list_voices()
        en_voices = [
            {"name": v["ShortName"], "gender": v["Gender"], "locale": v["Locale"]}
            for v in voices
            if v["Locale"].startswith("en")
        ]
        return en_voices
    except Exception as e:
        logger.error(f"Failed to list voices: {e}")
        return []
