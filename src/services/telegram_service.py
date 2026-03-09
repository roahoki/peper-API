"""Telegram Bot API helpers.

Thin wrapper around the Telegram sendMessage endpoint so other services
don't need to know about HTTP details.
"""

from __future__ import annotations

import os

import httpx

_BASE = "https://api.telegram.org/bot{token}"


def _bot_url(path: str) -> str:
    token = os.environ["TELEGRAM_BOT_TOKEN"]
    return f"{_BASE.format(token=token)}/{path}"


async def send_message(chat_id: int, text: str) -> None:
    """Send a text message to a Telegram chat."""
    async with httpx.AsyncClient() as client:
        await client.post(
            _bot_url("sendMessage"),
            json={"chat_id": chat_id, "text": text},
            timeout=10,
        )


async def download_file(file_id: str) -> bytes:
    """Download a file from Telegram CDN and return its raw bytes."""
    async with httpx.AsyncClient() as client:
        # Step 1: resolve file_id → file_path
        resp = await client.get(_bot_url("getFile"), params={"file_id": file_id}, timeout=10)
        resp.raise_for_status()
        file_path = resp.json()["result"]["file_path"]

        # Step 2: download the actual file
        token = os.environ["TELEGRAM_BOT_TOKEN"]
        download_url = f"https://api.telegram.org/file/bot{token}/{file_path}"
        file_resp = await client.get(download_url, timeout=30)
        file_resp.raise_for_status()
        return file_resp.content
