from typing import List, Dict, Optional
import asyncio

from app.services.settings import settings
from app.services.cache import cache
from app.services.logger import get_logger

logger = get_logger("research.scraper")


async def scrape_url(url: str) -> Optional[str]:
    """Extract clean article text from a URL using Trafilatura."""
    cache_key = f"scrape:{url}"
    cached = cache.get(cache_key)
    if cached:
        return cached

    try:
        import trafilatura
        import httpx

        loop = asyncio.get_event_loop()

        async def _fetch():
            async with httpx.AsyncClient(
                timeout=10,
                headers={
                    "User-Agent": (
                        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                        "AppleWebKit/537.36"
                    )
                },
                follow_redirects=True,
            ) as client:
                r = await client.get(url)
                return r.text if r.status_code == 200 else None

        html = await _fetch()
        if not html:
            return None

        def _extract(html_content):
            return trafilatura.extract(
                html_content,
                include_links=False,
                include_images=False,
                include_tables=True,
                no_fallback=False,
            )

        text = await loop.run_in_executor(None, _extract, html)

        if text:
            # Truncate to avoid huge contexts
            text = text[:4000]
            cache.set(cache_key, text, ttl=3600)
            logger.debug(f"Scraped {url} → {len(text)} chars")
        else:
            logger.warning(f"Trafilatura returned nothing for {url}")

        return text

    except Exception as e:
        logger.error(f"Scrape failed for {url}: {e}")
        return None


async def scrape_urls(urls: List[str]) -> List[Dict[str, str]]:
    """Scrape multiple URLs concurrently."""
    tasks = [scrape_url(url) for url in urls[: settings.MAX_SCRAPE_PAGES]]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    scraped = []
    for url, text in zip(urls, results):
        if isinstance(text, str) and text:
            scraped.append({"url": url, "content": text})
        elif isinstance(text, Exception):
            logger.warning(f"Scrape task exception for {url}: {text}")

    logger.info(f"Scraped {len(scraped)}/{len(urls)} URLs successfully")
    return scraped
