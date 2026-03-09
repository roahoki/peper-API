#!/usr/bin/env python3
"""One-time script to authorize the bot to write to Google Sheets.

Run this ONCE before starting the server:
  python scripts/auth_sheets.py

It will print a URL — open it in your browser, authorize with your Google
account, and paste back the code. The token is saved to sheets_token.json
and the server will use it automatically from then on (auto-refreshing).
"""

import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).parent.parent
CLIENT_SECRET_FILE = ROOT / "oauth_client.json"
TOKEN_FILE = ROOT / "sheets_token.json"
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]


def main() -> None:
    if not CLIENT_SECRET_FILE.exists():
        print(f"[error] {CLIENT_SECRET_FILE} not found.")
        print("  Download the OAuth client JSON from GCP Console and place it in the project root.")
        sys.exit(1)

    try:
        from google_auth_oauthlib.flow import InstalledAppFlow
    except ImportError:
        print("[error] google-auth-oauthlib is not installed.")
        print("  Run: pip install google-auth-oauthlib")
        sys.exit(1)

    print("Starting OAuth flow for Google Sheets...")
    print("A URL will appear below. Open it in your browser and authorize access.\n")

    flow = InstalledAppFlow.from_client_secrets_file(str(CLIENT_SECRET_FILE), SCOPES)

    # open_browser=False prints the URL without trying to open it automatically.
    # WSL2 forwards localhost ports to Windows, so the browser redirect lands here.
    creds = flow.run_local_server(port=0, open_browser=False)

    TOKEN_FILE.write_text(creds.to_json())
    print(f"\n[ok] Token saved to {TOKEN_FILE}")
    print("You can now start the server with 'make tunnel'.")


if __name__ == "__main__":
    main()
