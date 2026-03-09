"""Whisper transcription service.

Downloads a voice note (.ogg) from Telegram and transcribes it using the
OpenAI Whisper API. Returns the transcript as a plain string.
"""

from __future__ import annotations

import io

from openai import AsyncOpenAI

from src.services.telegram_service import download_file

_client = AsyncOpenAI()  # reads OPENAI_API_KEY from env automatically


async def transcribe_voice(file_id: str) -> str:
    """Download the voice note identified by file_id and return its transcript."""
    raw = await download_file(file_id)

    # Wrap bytes in a file-like object — Whisper accepts .ogg natively
    audio = io.BytesIO(raw)
    audio.name = "voice.ogg"

    transcription = await _client.audio.transcriptions.create(
        model="whisper-1",
        file=audio,
        language="es",
    )
    return transcription.text
