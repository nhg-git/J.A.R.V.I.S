from typing import AsyncGenerator, List, Dict, Any, Optional
import asyncio

from app.services.settings import settings
from app.services.logger import get_logger

logger = get_logger("llm.provider")


# ─────────────────────────────────────────────────────────────
# Ollama Provider  (free, local)
# ─────────────────────────────────────────────────────────────

async def stream_ollama(
    messages: List[Dict[str, str]],
    model: Optional[str] = None,
) -> AsyncGenerator[str, None]:
    """Stream tokens from a local Ollama model."""
    try:
        import ollama

        model = model or settings.OLLAMA_MODEL
        loop = asyncio.get_event_loop()

        def _sync_stream():
            return ollama.chat(
                model=model,
                messages=messages,
                stream=True,
                options={
                    "temperature": 0.7,
                    "num_ctx": 2048,      # smaller = faster
                    "num_predict": 600,   # cap response length for speed
                },
            )

        stream = await loop.run_in_executor(None, _sync_stream)
        for chunk in stream:
            token = chunk.get("message", {}).get("content", "")
            if token:
                yield token

    except ImportError:
        raise RuntimeError("ollama package not installed. Run: pip install ollama")
    except Exception as e:
        logger.error(f"Ollama streaming error: {e}")
        raise


async def chat_ollama(
    messages: List[Dict[str, str]],
    model: Optional[str] = None,
) -> str:
    """Single-shot chat with Ollama."""
    import ollama

    model = model or settings.OLLAMA_MODEL
    loop = asyncio.get_event_loop()

    def _sync_chat():
        return ollama.chat(model=model, messages=messages)

    response = await loop.run_in_executor(None, _sync_chat)
    return response["message"]["content"]


# ─────────────────────────────────────────────────────────────
# OpenAI Provider  (optional, paid)
# ─────────────────────────────────────────────────────────────

async def stream_openai(
    messages: List[Dict[str, str]],
    model: Optional[str] = None,
) -> AsyncGenerator[str, None]:
    """Stream tokens from OpenAI."""
    try:
        from openai import AsyncOpenAI

        client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        model = model or settings.OPENAI_MODEL

        async with client.chat.completions.stream(
            model=model,
            messages=messages,
            temperature=0.7,
        ) as stream:
            async for text in stream.text_stream:
                if text:
                    yield text

    except ImportError:
        raise RuntimeError("openai package not installed. Run: pip install openai")
    except Exception as e:
        logger.error(f"OpenAI streaming error: {e}")
        raise


async def chat_openai(
    messages: List[Dict[str, str]],
    model: Optional[str] = None,
) -> str:
    """Single-shot chat with OpenAI."""
    from openai import AsyncOpenAI

    client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
    model = model or settings.OPENAI_MODEL

    response = await client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0.7,
    )
    return response.choices[0].message.content


# ─────────────────────────────────────────────────────────────
# Unified interface
# ─────────────────────────────────────────────────────────────

async def stream_chat(
    messages: List[Dict[str, str]],
) -> AsyncGenerator[str, None]:
    """Stream chat using the configured provider."""
    provider = settings.LLM_PROVIDER.lower()
    logger.debug(f"Streaming via {provider} | messages={len(messages)}")

    if provider == "ollama":
        async for token in stream_ollama(messages):
            yield token
    elif provider == "openai":
        if not settings.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY not set in .env")
        async for token in stream_openai(messages):
            yield token
    else:
        raise ValueError(f"Unknown LLM provider: {provider}")


async def single_chat(messages: List[Dict[str, str]]) -> str:
    """Non-streaming single response."""
    provider = settings.LLM_PROVIDER.lower()

    if provider == "ollama":
        return await chat_ollama(messages)
    elif provider == "openai":
        return await chat_openai(messages)
    else:
        raise ValueError(f"Unknown LLM provider: {provider}")


async def check_provider_health() -> dict[str, Any]:
    """Check if the LLM provider is reachable."""
    try:
        if settings.LLM_PROVIDER == "ollama":
            import httpx
            async with httpx.AsyncClient() as client:
                r = await client.get(
                    f"{settings.OLLAMA_BASE_URL}/api/tags", timeout=5
                )
                models = [m["name"] for m in r.json().get("models", [])]
                return {
                    "status": "ok",
                    "provider": "ollama",
                    "model": settings.OLLAMA_MODEL,
                    "available_models": models,
                }
        else:
            return {
                "status": "ok",
                "provider": "openai",
                "model": settings.OPENAI_MODEL,
            }
    except Exception as e:
        return {"status": "error", "provider": settings.LLM_PROVIDER, "error": str(e)}
