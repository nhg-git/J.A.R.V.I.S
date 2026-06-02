from typing import List, Dict


def format_sources(search_results: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """
    Format raw search results into clean source objects for the frontend.
    """
    sources = []
    for i, result in enumerate(search_results, 1):
        url = result.get("url", "")
        title = result.get("title", f"Source {i}")
        snippet = result.get("snippet", "")

        sources.append({
            "index": i,
            "title": title,
            "url": url,
            "snippet": snippet[:200] + "..." if len(snippet) > 200 else snippet,
            "domain": _extract_domain(url),
        })

    return sources


def _extract_domain(url: str) -> str:
    try:
        from urllib.parse import urlparse
        parsed = urlparse(url)
        domain = parsed.netloc.replace("www.", "")
        return domain
    except Exception:
        return url
