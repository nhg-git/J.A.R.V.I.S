from typing import List, Dict
from app.llm.prompts import RESEARCH_SYSTEM_PROMPT
from app.services.logger import get_logger

logger = get_logger("research.summarize")

MAX_SNIPPET_LEN = 400
MAX_SCRAPED_LEN = 2000


def synthesise_research(
    original_query: str,
    search_results: List[Dict[str, str]],
    scraped_content: List[Dict[str, str]],
) -> str:
    """
    Build a rich research prompt that instructs the LLM to synthesise
    the gathered web content into a useful answer.
    """
    lines = [
        f"RESEARCH QUERY: {original_query}",
        "",
        "═══════════════════════════════════════",
        "GATHERED INTELLIGENCE:",
        "═══════════════════════════════════════",
    ]

    # ── Search snippets ──────────────────────────────────────
    lines.append("\n── SEARCH SNIPPETS ──")
    for i, r in enumerate(search_results[:5], 1):
        title = r.get("title", "Unknown")
        url = r.get("url", "")
        snippet = r.get("snippet", "")[:MAX_SNIPPET_LEN]
        lines.append(f"\n[{i}] {title}")
        lines.append(f"    URL: {url}")
        if snippet:
            lines.append(f"    {snippet}")

    # ── Scraped full content ─────────────────────────────────
    if scraped_content:
        lines.append("\n── FULL ARTICLE CONTENT ──")
        for item in scraped_content[:3]:
            url = item.get("url", "")
            content = item.get("content", "")[:MAX_SCRAPED_LEN]
            lines.append(f"\n--- Source: {url} ---")
            lines.append(content)

    lines += [
        "",
        "═══════════════════════════════════════",
        "INSTRUCTIONS:",
        "Using only the intelligence above, answer the research query in full.",
        "Stay in your JARVIS persona.",
        "End with a SOURCES section listing [number] Title — URL for each used source.",
    ]

    prompt = "\n".join(lines)
    logger.debug(f"Research prompt built: {len(prompt)} chars")
    return prompt
