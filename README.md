# peper-API

Backend API for **WiVer Bot** — a Telegram-based personal expense manager powered by an LLM. Users interact via voice or text messages in natural language; the bot interprets those messages, records transactions, and syncs everything to a Google Spreadsheet.

---

## Architecture overview

```
Telegram (voice/text)
        │
        ▼
   peper-API  (FastAPI)
        │
        ├──► LLM model       (intent parsing & NLU)
        │
        └──► Google Sheets   (persistent expense storage)
```

---

## Tech stack

| Layer | Technology |
|---|---|
| API framework | FastAPI + Uvicorn |
| Linter / formatter | Ruff |
| Commit conventions | Commitizen (conventional commits) |
| Messaging | Telegram Bot API |
| AI / NLU | LLM model (OpenAI / Anthropic / local) |
| Storage | Google Sheets via Google API |
| Config | python-dotenv |

---

## Project structure

```
peper-API/
├── src/
│   └── main.py          # FastAPI app entry point
├── requirements.txt     # Production dependencies
├── requirements-dev.txt # Dev/tooling dependencies
├── pyproject.toml       # Ruff + Commitizen configuration
├── Makefile             # Developer shortcuts
└── .env                 # Secret keys — never commit this file
```

---

## Getting started

### 1. Clone and set up the environment

```bash
git clone https://github.com/roahoki/peper-API.git
cd peper-API
make install-dev
```

### 2. Configure environment variables

Copy the example and fill in your credentials:

```bash
cp .env.example .env
```

Required variables:

```env
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
OPENAI_API_KEY=your_llm_api_key          # or equivalent for your LLM provider
GOOGLE_CREDENTIALS_PATH=google_credentials.json
SPREADSHEET_ID=your_google_spreadsheet_id
```

### 3. Run the development server

```bash
make dev
```

The API will be available at `http://localhost:8000`.  
Interactive docs: `http://localhost:8000/docs`

---

## Available `make` targets

```
make install       Install production dependencies
make install-dev   Install production + dev/tooling dependencies
make dev           Start server with hot-reload (port 8000)
make lint          Check code with ruff (read-only)
make fix           Auto-fix lint issues with ruff
make format        Format code with ruff formatter
make check         Lint + format check without changes (CI-safe)
make commit        Interactive conventional commit prompt (commitizen)
make bump          Bump version based on commit history + update CHANGELOG
make changelog     Regenerate CHANGELOG.md
make clean         Remove __pycache__ and .ruff_cache
```

---

## Commit conventions

This project follows [Conventional Commits](https://www.conventionalcommits.org/). Use `make commit` to open the interactive commitizen prompt instead of writing commits manually.

Common types: `feat`, `fix`, `docs`, `refactor`, `chore`, `test`

---

## API endpoints

| Method | Path | Description |
|---|---|---|
| GET | `/health` | Health check |

> More endpoints will be added as the project grows.

---

## Maintainer

Joaquín Peralta ~ roahoki

