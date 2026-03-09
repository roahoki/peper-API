# peper-API — WiVer Bot Backend

Backend API for **WiVer**, an automated expense tracking bot for **Peper** (logistics company). Users record daily business expenses via natural language — text or voice notes — in Telegram. The system extracts structured data using an LLM and appends it to a Google Spreadsheet used as a live dashboard.

---

## Architecture overview

```
Telegram user (text or voice note)
        │
        ▼
 POST /webhook  (FastAPI)
        │
        ├── [voice] Download .ogg → Whisper API → transcript text
        │
        ├──────────────────────────────────────────────────────────
        │   Claude (Anthropic API)
        │   System prompt injects: categories, fleet, workers list
        │   Returns: strict JSON { fecha, categoría, monto, ... }
        │──────────────────────────────────────────────────────────
        │
        ├──► gspread → append row to Google Sheets "Gastos" tab
        │
        └──► Telegram API → send Spanish confirmation to chat
```

---

## Tech stack

| Layer | Technology |
|---|---|
| API framework | FastAPI + Uvicorn |
| Messaging | Telegram Bot API |
| LLM / data extraction | Anthropic Claude (claude-3-5-sonnet) |
| Audio transcription | OpenAI Whisper API |
| Storage | Google Sheets (`gspread` + GCP Service Account) |
| Linter / formatter | Ruff |
| Commit conventions | Commitizen (conventional commits) |
| Local tunnel | ngrok |
| Containerization | Docker |
| Deployment | Google Cloud Run |
| CI/CD | GitHub Actions |
| Config | python-dotenv |

---

## Project structure

```
peper-API/
├── src/
│   ├── main.py              # FastAPI app entry point
│   ├── routers/             # Route handlers (webhook, etc.)
│   ├── services/            # Business logic (claude, sheets, whisper)
│   └── models/              # Pydantic schemas
├── docs/                    # Private planning docs (gitignored)
│   ├── PROJECT.md
│   └── TODO.md
├── .github/workflows/       # CI/CD pipeline
├── Dockerfile
├── requirements.txt         # Production dependencies
├── requirements-dev.txt     # Dev/tooling dependencies
├── pyproject.toml           # Ruff + Commitizen configuration
├── Makefile                 # Developer shortcuts
├── .env                     # Secret keys — never commit this file
└── .env.example             # Template for required env vars
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

```bash
cp .env.example .env
```

Required variables:

```env
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
ANTHROPIC_API_KEY=your_anthropic_api_key
OPENAI_API_KEY=your_openai_api_key          # used for Whisper transcription
GOOGLE_CREDENTIALS_PATH=google_credentials.json
SPREADSHEET_ID=your_google_spreadsheet_id
```

### 3. Run the development server

```bash
make dev
```

API available at `http://localhost:8000` — interactive docs at `http://localhost:8000/docs`.

### 4. Expose locally with ngrok (webhook testing)

```bash
ngrok http 8000
# Then register the webhook:
# https://api.telegram.org/bot<TOKEN>/setWebhook?url=<NGROK_URL>/webhook
```

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

## Google Sheets schema

The bot writes one row per expense to the `Gastos` sheet:

| Col | Field | Notes |
|---|---|---|
| A | ID | UUID / timestamp hash |
| B | Fecha | `YYYY-MM-DD` |
| C | Categoría | Combustible · Mecánico · Repuestos · Sueldos · Peajes · Viáticos |
| D | Monto | Numeric |
| E | Vehículo | Truck/trailer name or `null` |
| F | Trabajador | Worker name or `null` |
| G | Descripción | LLM-generated summary |
| H | Estado | Always `"Pendiente"` on creation |

---

## Commit conventions

This project follows [Conventional Commits](https://www.conventionalcommits.org/). Use `make commit` instead of `git commit` directly.

Common types: `feat`, `fix`, `docs`, `refactor`, `chore`, `test`

---

## API endpoints

| Method | Path | Description |
|---|---|---|
| GET | `/health` | Health check |
| POST | `/webhook` | Telegram webhook receiver |

---

## License

MIT
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

