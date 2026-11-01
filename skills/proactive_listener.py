"""Browser account creator.

Uruchamia automatyzację w przeglądarce, jeśli istnieje gotowy skrypt.
"""
import json
import subprocess
import sys
from pathlib import Path

SCRIPT_PATH = Path("scripts/create_tiktok_account_playwright.py")


def run(arg: str = "") -> str:
    if not arg:
        return json.dumps({"error": "usage: auto|email|password or info"}, ensure_ascii=False)
    parts = [p.strip() for p in arg.split("|")]
    cmd = parts[0].lower()

    if cmd == "info":
        return json.dumps({"script": str(SCRIPT_PATH), "exists": SCRIPT_PATH.exists()}, ensure_ascii=False)

    if cmd == "auto":
        if len(parts) < 3:
            return json.dumps({"error": "usage: auto|email|password"}, ensure_ascii=False)
        email = parts[1]
        password = parts[2]
        if not SCRIPT_PATH.exists():
            return json.dumps({"error": "script not found", "script": str(SCRIPT_PATH)}, ensure_ascii=False)
        try:
            subprocess.check_call([sys.executable, str(SCRIPT_PATH), "--email", email, "--password", password])
            return json.dumps({"status": "launched", "email": email}, ensure_ascii=False)
        except Exception as exc:
            return json.dumps({"error": str(exc)}, ensure_ascii=False)

    return json.dumps({"error": "unknown command"}, ensure_ascii=False)
