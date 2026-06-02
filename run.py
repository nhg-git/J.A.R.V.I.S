#!/usr/bin/env python3
"""
╔═══════════════════════════════════════════════════════╗
║           J.A.R.V.I.S  —  Launcher                   ║
║   Just A Rather Very Intelligent System               ║
╚═══════════════════════════════════════════════════════╝

Usage:
  python run.py                # Start the backend server
  python run.py --check        # Check all dependencies
  python run.py --setup        # First-time setup guide
"""

import sys
import os
import subprocess
import argparse
from pathlib import Path

# Make sure we're running from the project root
os.chdir(Path(__file__).parent)
sys.path.insert(0, str(Path(__file__).parent))


def check_python():
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 10):
        print("✗  Python 3.10+ required. You have:", sys.version)
        sys.exit(1)
    print(f"✓  Python {version.major}.{version.minor}.{version.micro}")


def check_dependencies():
    print("\n── Checking Python packages ──")
    packages = [
        ("fastapi",            "FastAPI"),
        ("uvicorn",            "Uvicorn"),
        ("sqlalchemy",         "SQLAlchemy"),
        ("pydantic_settings",  "Pydantic Settings"),
        ("duckduckgo_search",  "DuckDuckGo Search"),
        ("trafilatura",        "Trafilatura (scraper)"),
        ("edge_tts",           "Edge TTS (free voice)"),
        ("faster_whisper",     "Faster Whisper (STT)"),
    ]
    all_ok = True
    for module, name in packages:
        try:
            __import__(module)
            print(f"  ✓  {name}")
        except ImportError:
            print(f"  ✗  {name}  ← missing, run: pip install -r requirements.txt")
            all_ok = False
    return all_ok


def check_ollama():
    print("\n── Checking Ollama ──")
    try:
        result = subprocess.run(
            ["ollama", "list"], capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0:
            lines = [l for l in result.stdout.strip().split("\n") if l]
            print(f"  ✓  Ollama running — {len(lines)-1} model(s) available")
            for line in lines[1:]:
                print(f"       {line.split()[0]}")
            return True
        else:
            print("  ✗  Ollama not running")
            return False
    except (FileNotFoundError, subprocess.TimeoutExpired):
        print("  ✗  Ollama not installed → https://ollama.com")
        return False


def check_env():
    print("\n── Checking .env ──")
    env_path = Path(".env")
    if not env_path.exists():
        example = Path(".env.example")
        if example.exists():
            import shutil
            shutil.copy(example, env_path)
            print("  ✓  .env created from .env.example")
        else:
            print("  ✗  No .env file found")
            return False
    else:
        print("  ✓  .env present")
    return True


def setup_guide():
    print("""
╔══════════════════════════════════════════════════════════════╗
║  J.A.R.V.I.S  —  First-Time Setup Guide                     ║
╚══════════════════════════════════════════════════════════════╝

STEP 1 — Install Python dependencies
──────────────────────────────────────
  pip install -r requirements.txt

STEP 2 — Install Ollama (free local AI)
──────────────────────────────────────
  → Go to https://ollama.com and install for your OS
  → Then pull a model:
      ollama pull llama3.2          # Good balance (~2 GB)
      ollama pull llama3.2:1b       # Smaller, faster   (~1 GB)
      ollama pull mistral           # Alternative

STEP 3 — Configure .env
──────────────────────────────────────
  Copy .env.example to .env (already done by run.py if missing)
  Edit .env if you want to change model or voice settings.

STEP 4 — Install frontend dependencies
──────────────────────────────────────
  cd frontend
  npm install
  cd ..

STEP 5 — Run everything
──────────────────────────────────────
  Terminal 1:  python run.py          # Backend
  Terminal 2:  cd frontend && npm run dev   # Frontend

  Then open: http://localhost:5173

OPTIONAL — Use OpenAI instead of Ollama
──────────────────────────────────────
  In .env:  LLM_PROVIDER=openai
            OPENAI_API_KEY=sk-...
""")


def start_server():
    from app.services.settings import settings

    print(f"""
╔══════════════════════════════════════════════════════════════╗
║  J.A.R.V.I.S  —  Starting Backend                           ║
╚══════════════════════════════════════════════════════════════╝
  Backend  → http://{settings.HOST}:{settings.PORT}
  API docs → http://localhost:{settings.PORT}/docs
  Frontend → run  cd frontend && npm run dev  in another terminal
""")

    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        reload_excludes=["data/*", "*.db"],
        log_level="warning",
    )


def main():
    parser = argparse.ArgumentParser(description="J.A.R.V.I.S launcher")
    parser.add_argument("--check", action="store_true", help="Check all dependencies")
    parser.add_argument("--setup", action="store_true", help="Show setup guide")
    args = parser.parse_args()

    if args.setup:
        setup_guide()
        return

    if args.check:
        check_python()
        check_env()
        ok = check_dependencies()
        check_ollama()
        print("\n" + ("✅ All checks passed — run: python run.py" if ok else "⚠  Some packages missing"))
        return

    # Default: start the server
    check_env()
    start_server()


if __name__ == "__main__":
    main()
