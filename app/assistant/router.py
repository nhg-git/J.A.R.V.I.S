from typing import Literal
import re

from app.services.logger import get_logger

logger = get_logger("router")

# Message type literal
IntentType = Literal["chat", "research", "revision", "code"]

# ─────────────────────────────────────────────────────────────
# Keyword-based fast routing (no LLM call needed)
# ─────────────────────────────────────────────────────────────

RESEARCH_TRIGGERS = [
    r"\b(latest|recent|current|today|now|2024|2025|2026)\b",
    r"\b(news|update|announce|release|launch|new version)\b",
    r"\b(who is|who are|what is .{1,20} doing)\b",
    r"\b(price of|stock|weather|score|standings)\b",
    r"\b(search|find|look up|research|investigate)\b",
    r"\b(what happened|when did|how many .{0,20} are there)\b",
]

CODE_TRIGGERS = [
    r"\b(code|function|class|debug|error|bug|syntax|algorithm)\b",
    r"\b(python|javascript|typescript|rust|go|java|c\+\+|sql)\b",
    r"\b(write|fix|implement|refactor|explain this code)\b",
    r"```",
    r"\bdef \b|\bclass \b|\bconst \b|\blet \b|\bfunction \b",
]

REVISION_TRIGGERS = [
    r"\b(proofread|revise|edit|improve|rephrase|rewrite|fix my)\b",
    r"\b(grammar|spelling|punctuation|sentence|paragraph)\b",
    r"\b(make this better|improve this|polish|clean up)\b",
    r"\b(essay|email|letter|report|summary|document)\b.*\b(check|review|edit)\b",
]


def _matches_any(text: str, patterns: list[str]) -> bool:
    text_lower = text.lower()
    return any(re.search(p, text_lower) for p in patterns)


def route_intent(message: str) -> IntentType:
    """
    Fast keyword-based intent routing.
    Returns the intent type without making an LLM call.
    """
    # Check code first (most specific)
    if _matches_any(message, CODE_TRIGGERS):
        logger.debug(f"Routed → code  | msg='{message[:60]}'")
        return "code"

    # Check revision
    if _matches_any(message, REVISION_TRIGGERS):
        logger.debug(f"Routed → revision | msg='{message[:60]}'")
        return "revision"

    # Check research
    if _matches_any(message, RESEARCH_TRIGGERS):
        logger.debug(f"Routed → research | msg='{message[:60]}'")
        return "research"

    # Default: chat
    logger.debug(f"Routed → chat | msg='{message[:60]}'")
    return "chat"


def is_research_query(message: str) -> bool:
    return route_intent(message) == "research"
