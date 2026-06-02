from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

from app.assistant.memory import (
    get_recent_conversations,
    get_conversation_messages,
    create_conversation,
)
from app.llm.provider import check_provider_health

router = APIRouter(prefix="/api", tags=["chat"])


class NewConversationResponse(BaseModel):
    conversation_id: str


@router.post("/conversations", response_model=NewConversationResponse)
async def new_conversation(title: Optional[str] = None):
    """Create a new conversation session."""
    cid = create_conversation(title)
    return {"conversation_id": cid}


@router.get("/conversations")
async def list_conversations(limit: int = 20):
    """Return recent conversations."""
    return get_recent_conversations(limit)


@router.get("/conversations/{conversation_id}/messages")
async def get_messages(conversation_id: str):
    """Return all messages in a conversation."""
    messages = get_conversation_messages(conversation_id)
    if not messages:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return messages


@router.get("/health")
async def health_check():
    """System health check."""
    llm_status = await check_provider_health()
    return {
        "status": "online",
        "jarvis": "J.A.R.V.I.S operational",
        "llm": llm_status,
    }
