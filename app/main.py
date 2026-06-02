from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from pathlib import Path

from app.database.db import init_db
from app.api.chat import router as chat_router
from app.api.voice import router as voice_router
from app.api.websocket import jarvis_websocket
from app.services.settings import settings
from app.services.logger import get_logger

logger = get_logger("main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    logger.info("=" * 60)
    logger.info(f"  {settings.APP_NAME} v{settings.APP_VERSION} — INITIALISING")
    logger.info("=" * 60)

    # Initialise database
    init_db()

    logger.info(f"  LLM Provider : {settings.LLM_PROVIDER.upper()}")
    logger.info(f"  LLM Model    : {settings.OLLAMA_MODEL if settings.LLM_PROVIDER == 'ollama' else settings.OPENAI_MODEL}")
    logger.info(f"  Voice (TTS)  : {settings.TTS_VOICE if settings.ENABLE_TTS else 'DISABLED'}")
    logger.info(f"  Listening    : http://{settings.HOST}:{settings.PORT}")
    logger.info("=" * 60)
    logger.info("  ✅ J.A.R.V.I.S ONLINE — Ready to assist, sir.")
    logger.info("=" * 60)

    yield

    logger.info("J.A.R.V.I.S powering down...")


# ── Create app ────────────────────────────────────────────────
app = FastAPI(
    title="J.A.R.V.I.S",
    description="Just A Rather Very Intelligent System",
    version=settings.APP_VERSION,
    lifespan=lifespan,
    docs_url="/docs" if settings.DEBUG else None,
)

# ── CORS ──────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── REST API routers ──────────────────────────────────────────
app.include_router(chat_router)
app.include_router(voice_router)

# ── WebSocket endpoint ────────────────────────────────────────
from fastapi import WebSocket

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await jarvis_websocket(websocket)


# ── Root endpoint ─────────────────────────────────────────────
@app.get("/")
async def root():
    return {
        "system": "J.A.R.V.I.S",
        "status": "ONLINE",
        "version": settings.APP_VERSION,
        "message": "Good day, sir. All systems operational.",
    }


# ── __init__ files ────────────────────────────────────────────
for pkg in [
    "app", "app/services", "app/database", "app/llm",
    "app/assistant", "app/voice", "app/research", "app/api"
]:
    init_path = Path(__file__).parent.parent / pkg / "__init__.py"
    init_path.parent.mkdir(parents=True, exist_ok=True)
    if not init_path.exists():
        init_path.touch()
