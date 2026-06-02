from typing import List, Dict, Optional
import asyncio

from app.services.settings import settings
from app.services.cache import cache
from app.services.logger import get_logger

logger = get_logger("research.search")


async def web_search(
    query: str,
    max_results: int = None,
) -> List[Dict[str, str]]:
    """
    Search the web using DuckDuckGo (free, no API key).
    Returns a list of {title, url, snippet} dicts.
    """
    max_results = max_results or settings.MAX_SEARCH_RESULTS
    cache_key = f"search:{query}:{max_results}"

    cached = cache.get(cache_key)
    if cached:
        logger.debug(f"Search cache hit: '{query}'")
        return cached

    try:
        from duckduckgo_search import DDGS

        loop = asyncio.get_event_loop()

        def _sync_search():
            with DDGS() as ddgs:
                return list(
                    ddgs.text(
                        query,
                        max_results=max_results,
                        safesearch="moderate",
                    )
                )

        raw = await loop.run_in_executor(None, _sync_search)

        results = [
            {
                "title": r.get("title", ""),
                "url": r.get("href", ""),
                "snippet": r.get("body", ""),
            }
            for r in raw
            if r.get("href")
        ]

        logger.info(f"Search '{query}' → {len(results)} results")
        cache.set(cache_key, results, ttl=1800)  # 30 min cache
        return results

    except ImportError:
        logger.error("duckduckgo-search not installed")
        return []
    except Exception as e:
        logger.error(f"DuckDuckGo search error: {e}")
        return []
