from fastapi import APIRouter
from pydantic import BaseModel

from app.research.search import web_search
from app.research.citations import format_sources

router = APIRouter(prefix="/api/research", tags=["research"])


class SearchRequest(BaseModel):
    query: str
    max_results: int = 5


@router.post("/search")
async def search(request: SearchRequest):
    """Run a raw web search and return sources (no LLM synthesis)."""
    results = await web_search(request.query, request.max_results)
    return {
        "query": request.query,
        "results": format_sources(results),
        "count": len(results),
    }
