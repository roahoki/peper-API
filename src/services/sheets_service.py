"""Google Sheets service — appends validated expenses to the 'Gastos' worksheet.

Authentication reads sheets_token.json, generated once by running:
  python scripts/auth_sheets.py

The server never does interactive auth. On Cloud Run, the service account
attached to the instance is used automatically via ADC (no token file needed).

Required environment variable:
  SPREADSHEET_ID  — the long ID in the Google Sheets URL

Row schema (columns A–H):
  id | fecha | categoria | monto | vehiculo | trabajador | descripcion | estado
"""

from __future__ import annotations

import asyncio
import logging
import os
import uuid

import gspread
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

from src.models.expense import ExpenseRecord

logger = logging.getLogger(__name__)

_SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
_WORKSHEET_NAME = "Gastos"
_TOKEN_FILE = "sheets_token.json"


def _get_client() -> gspread.Client:
    if not os.path.exists(_TOKEN_FILE):
        raise RuntimeError(
            f"{_TOKEN_FILE} not found. "
            "Run 'python scripts/auth_sheets.py' once to authenticate."
        )

    creds = Credentials.from_authorized_user_file(_TOKEN_FILE, _SCOPES)
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        with open(_TOKEN_FILE, "w") as fh:
            fh.write(creds.to_json())

    return gspread.authorize(creds)


def _append_row_sync(expense: ExpenseRecord) -> None:
    """Synchronous: open the spreadsheet, find the worksheet, append a row."""
    spreadsheet_id = os.environ["SPREADSHEET_ID"]
    client = _get_client()
    sheet = client.open_by_key(spreadsheet_id)
    worksheet = sheet.worksheet(_WORKSHEET_NAME)

    row = [
        str(uuid.uuid4()),
        str(expense.fecha),
        expense.categoria,
        expense.monto,
        expense.vehiculo or "",
        expense.trabajador or "",
        expense.descripcion,
        expense.estado,
    ]
    worksheet.append_row(row, value_input_option="USER_ENTERED")
    logger.info("Row appended to Sheets: %s", row)


async def append_expense(expense: ExpenseRecord) -> None:
    """Append an expense row to the Google Sheet (runs sync call in a thread)."""
    await asyncio.to_thread(_append_row_sync, expense)
