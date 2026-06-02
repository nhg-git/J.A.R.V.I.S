from pydantic_settings import BaseSettings
from pathlib import Path
from typing import Optional, List

# Project root
BASE_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    # ── Application ───────────────────────────────────────────
    APP_NAME: str = "J.A.R.V.I.S"
    APP_VERSION: str = "2.0.0"
    DEBUG: bool = True
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # ── LLM Provider ──────────────────────────────────────────
    LLM_PROVIDER: str = "ollama"  # "ollama" or "openai"

    # Ollama (free local LLM)
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3.2"

    # OpenAI (optional)
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4o-mini"

    # ── Voice ─────────────────────────────────────────────────
    WHISPER_MODEL_SIZE: str = "base"       # tiny / base / small / medium
    TTS_VOICE: str = "en-US-GuyNeural"    # Edge TTS voice
    ENABLE_VOICE: bool = True
    ENABLE_TTS: bool = True

    # ── Research ──────────────────────────────────────────────
    BRAVE_API_KEY: Optional[str] = None
    MAX_SEARCH_RESULTS: int = 5
    MAX_SCRAPE_PAGES: int = 3
    RESEARCH_TIMEOUT: int = 30

    # ── Database ──────────────────────────────────────────────
    DB_PATH: str = str(BASE_DIR / "data" / "jarvis.db")

    # ── Memory / Context ──────────────────────────────────────
    CONTEXT_WINDOW_MESSAGES: int = 10     # Messages kept in LLM context
    MAX_STORED_MESSAGES: int = 200        # Messages stored in DB per session

    # ── CORS ──────────────────────────────────────────────────
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
    ]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


settings = Settings()
