from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel
from typing import Optional

from app.voice.tts import synthesise_speech, list_available_voices
from app.voice.stt import transcribe_base64_audio
from app.services.settings import settings

router = APIRouter(prefix="/api/voice", tags=["voice"])


class TTSRequest(BaseModel):
    text: str
    voice: Optional[str] = None


class STTRequest(BaseModel):
    audio: str  # base64 encoded audio


@router.post("/tts")
async def text_to_speech(request: TTSRequest):
    """Convert text to MP3 audio and return as bytes."""
    if not settings.ENABLE_TTS:
        raise HTTPException(status_code=503, detail="TTS is disabled")

    audio = await synthesise_speech(request.text, request.voice)
    if not audio:
        raise HTTPException(status_code=500, detail="TTS synthesis failed")

    return Response(content=audio, media_type="audio/mpeg")


@router.post("/stt")
async def speech_to_text(request: STTRequest):
    """Transcribe base64-encoded audio to text."""
    text = transcribe_base64_audio(request.audio)
    if not text:
        raise HTTPException(status_code=422, detail="Could not transcribe audio")
    return {"text": text}


@router.get("/voices")
async def get_voices():
    """Return available TTS voices."""
    voices = await list_available_voices()
    return {"voices": voices, "current": settings.TTS_VOICE}
