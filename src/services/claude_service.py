"""Claude service — expense extraction via Anthropic API.

Sends the user's text to Claude with a strict system prompt that knows
Peper's valid categories, vehicles, and workers. Claude must respond with
a JSON object matching one of two shapes:

  { "action": "record_expense", "expense": { ...ExpenseRecord fields... } }
  { "action": "ask_clarification", "question": "<Spanish question>" }

Returns a typed ClaudeResult (RecordExpenseAction | AskClarificationAction).
"""

from __future__ import annotations

import json
import logging
from datetime import date

import anthropic

from src.config.loader import business
from src.models.expense import (
    AskClarificationAction,
    ClaudeResult,
    ExpenseRecord,
    RecordExpenseAction,
)

logger = logging.getLogger(__name__)

_client = anthropic.AsyncAnthropic()  # reads ANTHROPIC_API_KEY from env

_MODEL = "claude-sonnet-4-20250514"
_MAX_TOKENS = 512


def _build_system_prompt() -> str:
    today = date.today().isoformat()
    categories = ", ".join(business.categories)
    vehicles = ", ".join(business.vehicles)
    workers = ", ".join(business.workers)

    return f"""You are an expense-logging assistant for Peper, a Chilean logistics company.
Today's date is {today}.

Your job is to extract a structured expense record from the user's message (which may be text
transcribed from a voice note in Chilean Spanish) and return a JSON object — nothing else.

## Valid values

- categories: {categories}
- vehicles: {vehicles}
- workers: {workers}

## Response contract

You MUST return one of these two JSON shapes, with no extra text or markdown:

### When you have enough information:
{{
  "action": "record_expense",
  "expense": {{
    "fecha": "YYYY-MM-DD",
    "categoria": "<one of the valid categories above>",
    "monto": <positive number in CLP>,
    "vehiculo": "<one of the valid vehicles, or null>",
    "trabajador": "<one of the valid workers, or null>",
    "descripcion": "<short description in Spanish>"
  }}
}}

### When critical information is missing (e.g. amount or category is ambiguous):
{{
  "action": "ask_clarification",
  "question": "<short clarifying question in Spanish>"
}}

## Rules
- Always use today's date ({today}) unless the message specifies another date.
- "monto" must be a positive number. If the user says "35 lucas", that is 35000.
  "lucas" = thousands of Chilean pesos (e.g. "500 lucas" = 500000).
- If the category is not in the valid list, pick the closest one or ask.
- If "vehiculo" or "trabajador" is not mentioned, return null for those fields.
- Never invent amounts. If the amount is missing or unclear, ask.
- Respond in JSON only. No prose, no markdown code fences."""


async def extract_expense(user_text: str) -> ClaudeResult:
    """Send user_text to Claude and return a typed ClaudeResult."""
    system_prompt = _build_system_prompt()

    message = await _client.messages.create(
        model=_MODEL,
        max_tokens=_MAX_TOKENS,
        system=system_prompt,
        messages=[{"role": "user", "content": user_text}],
    )

    raw = message.content[0].text.strip()
    logger.debug("Claude raw response: %s", raw)

    data = json.loads(raw)

    if data["action"] == "record_expense":
        expense = ExpenseRecord(**data["expense"])
        return RecordExpenseAction(action="record_expense", expense=expense)

    return AskClarificationAction(action="ask_clarification", question=data["question"])
