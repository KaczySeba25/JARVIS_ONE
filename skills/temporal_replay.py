"""Proactive listener gadget.

Rozpoznaje intencję z krótkich wejść i zapisuje preflight do data_vault/preflights.json.
"""
import json
import time
from pathlib import Path

DATA_VAULT = Path("data_vault")
DATA_VAULT.mkdir(exist_ok=True)
FILE = DATA_VAULT / "preflights.json"


def _read():
    if FILE.exists():
        try:
            return json.loads(FILE.read_text(encoding="utf-8"))
        except Exception:
            return []
    return []


def _write(items):
    FILE.write_text(json.dumps(items, indent=2, ensure_ascii=False), encoding="utf-8")


def run(query: str = "") -> str:
    if not query:
        return json.dumps({"error": "no query"}, ensure_ascii=False)
    q = query.lower()
    suggestion = {"action": "noop", "reason": "no preflight"}
    if "konto" in q or "account" in q or "utwórz konto" in q or "otworz konto" in q:
        suggestion = {"action": "prepare_email_and_task", "reason": "account creation detected", "timestamp": int(time.time())}
    elif "tiktok" in q:
        suggestion = {"action": "prepare_tiktok_browser_flow", "reason": "tiktok detected", "timestamp": int(time.time())}

    records = _read()
    records.append({"query": query, "suggestion": suggestion})
    _write(records)
    return json.dumps({"suggestion": suggestion}, ensure_ascii=False)
