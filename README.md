# J.A.R.V.I.S
### Just A Rather Very Intelligent System

```
     ██╗ █████╗ ██████╗ ██╗   ██╗██╗███████╗
     ██║██╔══██╗██╔══██╗██║   ██║██║██╔════╝
     ██║███████║██████╔╝██║   ██║██║███████╗
██   ██║██╔══██║██╔══██╗╚██╗ ██╔╝██║╚════██║
╚█████╔╝██║  ██║██║  ██║ ╚████╔╝ ██║███████║
 ╚════╝ ╚═╝  ╚═╝╚═╝  ╚═╝  ╚═══╝  ╚═╝╚══════╝
```

A personal AI assistant with a JARVIS-style terminal UI. Voice input, live web research,
conversation memory, and streaming responses — all **100% free** with local AI.

---

## Features

- **JARVIS personality** — formal, sharp, occasionally dry
- **Streaming responses** — token-by-token like a real terminal
- **Voice input** — speak your query (browser STT or Whisper)
- **Voice output** — JARVIS speaks back via Edge TTS (free)
- **Web research** — live DuckDuckGo search + article scraping
- **Conversation memory** — SQLite-backed history across sessions
- **Intent routing** — auto-detects chat / research / code / revision
- **CRT terminal aesthetic** — black, blue, glows, scanlines

---

## Tech Stack

| Layer    | Tool                              | Cost |
|----------|-----------------------------------|------|
| Frontend | React + Vite + vanilla CSS        | Free |
| Backend  | FastAPI + Python                  | Free |
| LLM      | Ollama (llama3.2 or similar)      | Free |
| Search   | DuckDuckGo Search API             | Free |
| Scraper  | Trafilatura + BeautifulSoup       | Free |
| STT      | Browser Web Speech API / Whisper  | Free |
| TTS      | Microsoft Edge TTS (edge-tts)     | Free |
| Database | SQLite                            | Free |

---

## Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+
- [Ollama](https://ollama.com) installed

---

### Step 1 — Clone / set up the folder

```bash
cd jarvis
```

---

### Step 2 — Install Python dependencies

```bash
pip install -r requirements.txt
```

---

### Step 3 — Install and configure Ollama

```bash
# Install from https://ollama.com, then pull a model:
ollama pull llama3.2          # Recommended (~2 GB)
ollama pull llama3.2:1b       # Smaller/faster if RAM is tight (~1 GB)
```

> Ollama runs silently in the background on Windows/Mac after install.
> On Linux: `ollama serve` in a terminal.

---

### Step 4 — Configure environment

```bash
# .env is auto-created from .env.example on first run
# Edit it if you want to change model or voice:
```

Key settings in `.env`:

```env
LLM_PROVIDER=ollama          # Use local Ollama (free)
OLLAMA_MODEL=llama3.2        # Match what you pulled above

TTS_VOICE=en-US-GuyNeural    # JARVIS voice — sounds great
WHISPER_MODEL_SIZE=base      # tiny/base/small (base is a good balance)
```

---

### Step 5 — Install frontend

```bash
cd frontend
npm install
cd ..
```

---

### Step 6 — Run

**Terminal 1 — Backend:**
```bash
python run.py
```

**Terminal 2 — Frontend:**
```bash
cd frontend
npm run dev
```

Open **http://localhost:5173** in your browser.

---

## Using JARVIS

| Action | How |
|--------|-----|
| Send a message | Type and press **Enter** |
| New line in input | **Shift + Enter** |
| Force web research | Click **⬡ SEARCH** or start with "search" / "latest" |
| Voice input | Click the 🎤 mic button, speak, click again to stop |
| View sources | Research panel appears on the right automatically |

### Example queries

```
What's the latest in quantum computing?          → research mode
Can you help me revise this paragraph: [text]    → revision mode
Write me a Python function to sort a dict        → code mode
Tell me about the Roman Empire                   → chat mode
search: latest AI news this week                 → forced research
```

---

## Checking everything is set up

```bash
python run.py --check
```

This verifies Python, packages, Ollama, and your `.env`.

---

## Optional — Use OpenAI instead of Ollama

If you want to use OpenAI (costs money but higher quality):

```env
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini
```

---

## Project Structure

```
jarvis/
├── app/
│   ├── main.py              # FastAPI entry point
│   ├── assistant/
│   │   ├── orchestrator.py  # Main brain — coordinates everything
│   │   ├── router.py        # Intent detection (chat/research/code/revision)
│   │   └── memory.py        # Conversation persistence
│   ├── llm/
│   │   ├── provider.py      # Ollama + OpenAI wrapper
│   │   └── prompts.py       # JARVIS system prompts
│   ├── research/
│   │   ├── search.py        # DuckDuckGo search
│   │   ├── scraper.py       # Article extraction (Trafilatura)
│   │   ├── summarize.py     # Research prompt builder
│   │   └── citations.py     # Source formatter
│   ├── voice/
│   │   ├── tts.py           # Edge TTS (free, great quality)
│   │   └── stt.py           # Faster Whisper (local STT)
│   ├── database/
│   │   ├── db.py            # SQLAlchemy engine
│   │   └── models.py        # Conversation + Message models
│   ├── api/
│   │   ├── chat.py          # REST endpoints
│   │   ├── voice.py         # Voice endpoints
│   │   └── websocket.py     # Real-time WebSocket handler
│   └── services/
│       ├── settings.py      # Config from .env
│       ├── logger.py        # Coloured logging
│       └── cache.py         # In-memory TTL cache
├── frontend/
│   └── src/
│       ├── components/
│       │   ├── Terminal.jsx       # Main terminal UI
│       │   ├── StatusBar.jsx      # Top HUD
│       │   ├── ResearchPanel.jsx  # Source sidebar
│       │   ├── TypingAnimation.jsx
│       │   └── VoiceIndicator.jsx
│       ├── hooks/
│       │   ├── useChat.js    # WebSocket + message state
│       │   └── useVoice.js   # Mic recording
│       └── pages/Home.jsx
├── data/                    # Auto-created: DB, logs, cache
├── run.py                   # Launcher
└── requirements.txt
```

---

## Troubleshooting

**"Ollama not running"** — Start Ollama (desktop app or `ollama serve`)

**"Model not found"** — Run `ollama pull llama3.2` in a terminal

**No voice output** — Check `ENABLE_TTS=true` in `.env`; Edge TTS needs internet

**Mic button not working** — Allow microphone in browser, use HTTPS or localhost

**Slow responses** — Try `OLLAMA_MODEL=llama3.2:1b` for the smaller, faster model

---

*"I have been a faithful assistant, and I will continue to be so."*
— J.A.R.V.I.S
