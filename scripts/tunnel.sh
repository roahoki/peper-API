#!/usr/bin/env bash
# tunnel.sh — Start uvicorn + ngrok and auto-register the Telegram webhook.
#
# Usage: make tunnel
# Requirements:
#   - ngrok installed and authenticated (ngrok config add-authtoken <token>)
#   - TELEGRAM_BOT_TOKEN set in .env or in the shell environment

set -euo pipefail

# ── Load .env if present ──────────────────────────────────────────────────────
if [[ -f ".env" ]]; then
    # Export only lines that look like KEY=VALUE (skip comments and blank lines)
    set -o allexport
    # shellcheck disable=SC1091
    source <(grep -E '^[A-Z_]+=.+' .env)
    set +o allexport
fi

# ── Validate required vars ────────────────────────────────────────────────────
if [[ -z "${TELEGRAM_BOT_TOKEN:-}" ]]; then
    echo "[error] TELEGRAM_BOT_TOKEN is not set."
    echo "        Add it to your .env file or export it in your shell."
    exit 1
fi

PORT=8000
NGROK_API="http://localhost:4040/api/tunnels"

# ── Start uvicorn in the background ──────────────────────────────────────────
echo "[tunnel] Starting uvicorn on port $PORT..."
.venv/bin/uvicorn src.main:app --reload --host 0.0.0.0 --port "$PORT" &
UVICORN_PID=$!

# ── Start ngrok in the background ─────────────────────────────────────────────
echo "[tunnel] Starting ngrok tunnel..."
ngrok http "$PORT" --log=stderr &
NGROK_PID=$!

# ── Graceful cleanup on exit ──────────────────────────────────────────────────
cleanup() {
    echo ""
    echo "[tunnel] Shutting down..."
    kill "$UVICORN_PID" "$NGROK_PID" 2>/dev/null || true
    wait "$UVICORN_PID" "$NGROK_PID" 2>/dev/null || true

    # Remove the webhook so Telegram stops sending requests to the dead tunnel
    echo "[tunnel] Removing Telegram webhook..."
    curl -s "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/deleteWebhook" > /dev/null
    echo "[tunnel] Webhook removed. Bye!"
}
trap cleanup EXIT INT TERM

# ── Wait for ngrok to be ready and get the public URL ────────────────────────
echo "[tunnel] Waiting for ngrok to be ready..."
NGROK_URL=""
for i in $(seq 1 15); do
    sleep 1
    NGROK_URL=$(
        curl -s "$NGROK_API" 2>/dev/null \
        | python3 -c "
import sys, json
try:
    tunnels = json.load(sys.stdin).get('tunnels', [])
    https = [t for t in tunnels if t['proto'] == 'https']
    print(https[0]['public_url'] if https else '')
except Exception:
    print('')
"
    )
    if [[ -n "$NGROK_URL" ]]; then
        break
    fi
    echo "[tunnel] Waiting... ($i/15)"
done

if [[ -z "$NGROK_URL" ]]; then
    echo "[error] Could not get ngrok public URL. Is ngrok authenticated?"
    exit 1
fi

WEBHOOK_URL="${NGROK_URL}/webhook"
echo "[tunnel] Public URL: $NGROK_URL"

# ── Register the webhook with Telegram ───────────────────────────────────────
echo "[tunnel] Registering webhook: $WEBHOOK_URL"
RESPONSE=$(curl -s "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/setWebhook?url=${WEBHOOK_URL}")
echo "[tunnel] Telegram response: $RESPONSE"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  WiVer is live!"
echo "  Webhook → $WEBHOOK_URL"
echo "  Docs    → http://localhost:$PORT/docs"
echo "  ngrok   → http://localhost:4040"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Press Ctrl+C to stop and remove webhook"
echo ""

# ── Keep alive — wait for uvicorn (foreground) ────────────────────────────────
wait "$UVICORN_PID"
