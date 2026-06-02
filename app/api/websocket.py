import json
import uuid
from typing import Optional

from fastapi import WebSocket, WebSocketDisconnect

from app.assistant.orchestrator import handle_message
from app.assistant.memory import create_conversation, get_conversation_messages
from app.voice.tts import text_to_base64_audio
from app.services.settings import settings
from app.services.logger import get_logger

logger = get_logger("api.websocket")


async def jarvis_websocket(websocket: WebSocket):
    """
    Main WebSocket endpoint for real-time JARVIS communication.

    Message protocol (client → server):
    ─────────────────────────────────────
    {
      "type": "chat" | "research" | "voice" | "ping" | "history",
      "content": "string",         # for chat/research
      "audio": "base64string",     # for voice
      "conversation_id": "uuid"    # optional, auto-created if missing
    }

    Message protocol (server → client):
    ─────────────────────────────────────
    { "type": "connected",  "conversation_id": "uuid" }
    { "type": "text_chunk", "content": "token text"   }
    { "type": "status",     "content": "status msg"   }
    { "type": "typing_start" }
    { "type": "research_sources", "sources": [...] }
    { "type": "audio",      "data": "base64 mp3"      }
    { "type": "voice_text", "content": "transcript"   }
    { "type": "history",    "messages": [...]          }
    { "type": "done"                                   }
    { "type": "error",      "content": "error msg"    }
    { "type": "pong" }
    """
    await websocket.accept()
    conversation_id: Optional[str] = None

    async def send(msg_type: str, content=None, **kwargs):
        """Helper — send a JSON message to the browser."""
        payload = {"type": msg_type}
        if content is not None:
            payload["content"] = content
        payload.update(kwargs)
        try:
            await websocket.send_json(payload)
        except Exception as e:
            logger.warning(f"Send failed ({msg_type}): {e}")

    logger.info("WebSocket connection established")

    try:
        while True:
            raw = await websocket.receive_text()

            try:
                data = json.loads(raw)
            except json.JSONDecodeError:
                await send("error", "Invalid JSON payload")
                continue

            msg_type = data.get("type", "chat")

            # ── Ping / Pong ──────────────────────────────────
            if msg_type == "ping":
                await send("pong")
                continue

            # ── Conversation init / resume ───────────────────
            if conversation_id is None:
                conversation_id = data.get("conversation_id") or create_conversation()
                await send("connected", conversation_id=conversation_id)
                logger.info(f"Session: {conversation_id[:8]}")

            # ── Load history ─────────────────────────────────
            if msg_type == "history":
                messages = get_conversation_messages(conversation_id)
                await send("history", messages=messages)
                continue

            # ── Voice (audio → transcribe → chat) ────────────
            if msg_type == "voice":
                b64_audio = data.get("audio", "")
                if not b64_audio:
                    await send("error", "No audio data received")
                    continue

                await send("status", "Processing audio input...")

                try:
                    from app.voice.stt import transcribe_base64_audio
                    transcript = transcribe_base64_audio(b64_audio)
                except Exception as e:
                    logger.error(f"STT error: {e}")
                    transcript = None

                if not transcript:
                    await send("error", "Could not transcribe audio. Please try again.")
                    continue

                # Echo the transcript back so the terminal shows what was said
                await send("voice_text", transcript)

                # Then process it as a chat message
                msg_type = "chat"
                data["content"] = transcript

            # ── Chat / Research ───────────────────────────────
            if msg_type in ("chat", "research"):
                content = data.get("content", "").strip()
                if not content:
                    await send("error", "Empty message")
                    continue

                force_research = msg_type == "research"

                # Run the orchestrator; it calls `send` internally for streaming
                full_response = await handle_message(
                    message=content,
                    conversation_id=conversation_id,
                    send=send,
                    force_research=force_research,
                )

                # Optional TTS
                if settings.ENABLE_TTS and full_response:
                    audio_b64 = await text_to_base64_audio(full_response)
                    if audio_b64:
                        await send("audio", data=audio_b64)

                continue

            # ── Unknown message type ──────────────────────────
            await send("error", f"Unknown message type: {msg_type}")

    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected | session={conversation_id}")
    except Exception as e:
        logger.error(f"WebSocket error: {e}", exc_info=True)
        try:
            await send("error", f"Internal error: {str(e)}")
        except Exception:
            pass
