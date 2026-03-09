import logging

from fastapi import APIRouter, Request

from src.models.expense import (
    AskClarificationAction,
    ExpenseRecord,
    RecordExpenseAction,
)
from src.services import claude_service, telegram_service, whisper_service

router = APIRouter()
logger = logging.getLogger(__name__)

# In-memory store for expenses awaiting user confirmation, keyed by chat_id.
_pending_expenses: dict[int, ExpenseRecord] = {}

_CONFIRM_WORDS = {
    "si",
    "sí",
    "confirmo",
    "yes",
    "dale",
    "ok",
    "bueno",
    "correcto",
    "✅",
}
_CANCEL_WORDS = {"no", "nop", "nope", "cancelar", "cancel", "descartar", "❌"}


def _is_confirmation(text: str) -> bool:
    return text.strip().lower() in _CONFIRM_WORDS


def _is_cancellation(text: str) -> bool:
    return text.strip().lower() in _CANCEL_WORDS


def _format_preview(expense: ExpenseRecord) -> str:
    """Preview shown to the user before they confirm the expense."""
    lines = [
        "🧾 Voy a registrar este gasto:",
        f"  📅 Fecha: {expense.fecha}",
        f"  🏷️  Categoría: {expense.categoria}",
        f"  💵 Monto: ${expense.monto:,.0f}",
    ]
    if expense.vehiculo:
        lines.append(f"  🚛 Vehículo: {expense.vehiculo}")
    else:
        lines.append("  🚛 Vehículo: no especificado")
    if expense.trabajador:
        lines.append(f"  👤 Trabajador: {expense.trabajador}")
    else:
        lines.append("  👤 Trabajador: no especificado")
    lines.append(f"  📝 {expense.descripcion}")
    lines.append("")
    lines.append("¿Confirmas? Responde *Sí* para registrar o *No* para cancelar.")
    return "\n".join(lines)


def _format_recorded(expense: ExpenseRecord) -> str:
    """Confirmation message sent after the user confirms."""
    lines = [
        "✅ Gasto registrado:",
        f"  📅 Fecha: {expense.fecha}",
        f"  🏷️  Categoría: {expense.categoria}",
        f"  💵 Monto: ${expense.monto:,.0f}",
    ]
    if expense.vehiculo:
        lines.append(f"  🚛 Vehículo: {expense.vehiculo}")
    if expense.trabajador:
        lines.append(f"  👤 Trabajador: {expense.trabajador}")
    lines.append(f"  📝 {expense.descripcion}")
    return "\n".join(lines)


@router.post("/webhook")
async def telegram_webhook(request: Request):
    """Receive all Telegram updates via webhook and orchestrate the AI pipeline.

    Flow:
      1. Extract text from the update (plain text or transcribed voice note).
      2. If there is a pending expense for this chat, handle sí/no confirmation.
      3. Otherwise send text to Claude for structured expense extraction.
      4a. record_expense  → store as pending, reply with preview asking for confirmation.
      4b. ask_clarification → reply with Claude's question so the user can provide more info.

    Always returns {"ok": True} with HTTP 200 to Telegram within 5 seconds.
    """
    payload = await request.json()
    logger.info("Telegram update received: %s", payload)

    message = payload.get("message") or payload.get("edited_message")
    if not message:
        return {"ok": True}

    chat_id: int = message["chat"]["id"]
    text: str | None = None

    # ── Voice note → Whisper transcript ──────────────────────────────────────
    if voice := message.get("voice"):
        try:
            text = await whisper_service.transcribe_voice(voice["file_id"])
            logger.info("Whisper transcript: %s", text)
        except Exception:
            logger.exception("Whisper transcription failed")
            await telegram_service.send_message(
                chat_id,
                "❌ No pude transcribir el audio. Intenta de nuevo o escribe el gasto.",
            )
            return {"ok": True}

    # ── Plain text message ────────────────────────────────────────────────────
    elif text_content := message.get("text"):
        text = text_content

    if not text:
        return {"ok": True}

    # ── Pending confirmation check ────────────────────────────────────────────
    if chat_id in _pending_expenses:
        pending = _pending_expenses[chat_id]
        if _is_confirmation(text):
            del _pending_expenses[chat_id]
            logger.info("Expense confirmed by user: %s", pending)
            # Phase 3: write to Google Sheets here
            await telegram_service.send_message(chat_id, _format_recorded(pending))
            return {"ok": True}
        if _is_cancellation(text):
            del _pending_expenses[chat_id]
            logger.info("Expense cancelled by user")
            await telegram_service.send_message(chat_id, "❌ Gasto cancelado.")
            return {"ok": True}
        # User sent something new — discard the old pending and process as new expense
        logger.info("New message while expense pending — discarding pending expense")
        del _pending_expenses[chat_id]

    # ── Claude extraction ─────────────────────────────────────────────────────
    try:
        result = await claude_service.extract_expense(text)
    except Exception:
        logger.exception("Claude extraction failed")
        await telegram_service.send_message(
            chat_id,
            "❌ Hubo un error al procesar el gasto. Intenta de nuevo.",
        )
        return {"ok": True}

    if isinstance(result, RecordExpenseAction):
        logger.info("Expense extracted, awaiting confirmation: %s", result.expense)
        _pending_expenses[chat_id] = result.expense
        await telegram_service.send_message(chat_id, _format_preview(result.expense))

    elif isinstance(result, AskClarificationAction):
        logger.info("Claude asking for clarification: %s", result.question)
        await telegram_service.send_message(chat_id, result.question)

    return {"ok": True}
