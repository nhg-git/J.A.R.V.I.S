from typing import AsyncGenerator, Callable, Awaitable, Optional
import asyncio

from app.assistant.memory import load_context, save_message
from app.assistant.router import route_intent
from app.llm.provider import stream_chat
from app.llm.prompts import JARVIS_SYSTEM_PROMPT
from app.services.logger import get_logger

logger = get_logger("orchestrator")

# Type for sending WebSocket events to the client
StatusCallback = Callable[[str, str], Awaitable[None]]  # (type, content)


async def handle_message(
    message: str,
    conversation_id: str,
    send: StatusCallback,
    force_research: bool = False,
) -> str:
    """
    Main entry point for processing a user message.

    Determines intent, runs the appropriate pipeline, streams the
    response back via `send`, and persists everything to the DB.

    Returns the full assistant response string.
    """
    # 1. Persist user message
    save_message(conversation_id, "user", message)

    # 2. Route intent
    intent = "research" if force_research else route_intent(message)
    logger.info(f"[{conversation_id[:8]}] intent={intent} | '{message[:60]}'")

    # 3. Dispatch to correct pipeline
    if intent == "research":
        full_response = await _research_pipeline(message, conversation_id, send)
    else:
        full_response = await _chat_pipeline(message, conversation_id, send, intent)

    # 4. Persist assistant response
    save_message(
        conversation_id,
        "assistant",
        full_response,
        message_type=intent,
        has_sources=(intent == "research"),
    )

    return full_response


# ─────────────────────────────────────────────────────────────
# Chat / Code / Revision pipeline
# ─────────────────────────────────────────────────────────────

async def _chat_pipeline(
    message: str,
    conversation_id: str,
    send: StatusCallback,
    intent: str,
) -> str:
    """Stream a direct LLM response for chat/code/revision messages."""

    context = load_context(conversation_id)

    # Add the current user message (it was saved but not yet in context)
    context.append({"role": "user", "content": message})

    full_response = ""
    try:
        await send("typing_start", "")
        async for token in stream_chat(context):
            full_response += token
            await send("text_chunk", token)
    except Exception as e:
        logger.error(f"Chat pipeline error: {e}")
        error_msg = (
            "I'm sorry, sir. I encountered an issue processing your request. "
            f"Error: {str(e)}"
        )
        await send("text_chunk", error_msg)
        return error_msg

    await send("done", "")
    return full_response


# ─────────────────────────────────────────────────────────────
# Research pipeline
# ─────────────────────────────────────────────────────────────

async def _research_pipeline(
    message: str,
    conversation_id: str,
    send: StatusCallback,
) -> str:
    """Run web research then synthesise with the LLM."""
    from app.research.search import web_search
    from app.research.scraper import scrape_urls
    from app.research.summarize import synthesise_research
    from app.research.citations import format_sources

    try:
        # Status updates
        await send("status", "Initiating search protocols...")
        await asyncio.sleep(0.1)

        # 1. Search
        results = await web_search(message)
        if not results:
            await send("status", "No results found. Falling back to knowledge base...")
            return await _chat_pipeline(message, conversation_id, send, "chat")

        await send(
            "status",
            f"Analysing {len(results)} source{'s' if len(results) > 1 else ''}...",
        )
        await send("research_sources", format_sources(results))

        # 2. Scrape top results
        urls = [r["url"] for r in results[:3] if r.get("url")]
        scraped = await scrape_urls(urls)

        await send("status", "Synthesising findings...")
        await asyncio.sleep(0.1)

        # 3. Build research context for LLM
        research_context = synthesise_research(message, results, scraped)

        # 4. Stream synthesis from LLM
        context = load_context(conversation_id)
        context.append({"role": "user", "content": research_context})

        full_response = ""
        await send("typing_start", "")
        async for token in stream_chat(context):
            full_response += token
            await send("text_chunk", token)

        await send("done", "")
        return full_response

    except Exception as e:
        logger.error(f"Research pipeline error: {e}")
        await send("status", "Research failed. Falling back to knowledge base...")
        return await _chat_pipeline(message, conversation_id, send, "chat")
