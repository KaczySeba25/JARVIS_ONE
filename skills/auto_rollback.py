"""Phantom Worker Gadget.

Tworzy izolowany profil roboczy do automatyzacji przeglądarki.
"""
import json
from pathlib import Path

DATA_VAULT = Path("data_vault")
DATA_VAULT.mkdir(exist_ok=True)
FILE = DATA_VAULT / "phantom_worker.json"


def _read():
    if FILE.exists():
        try:
            return json.loads(FILE.read_text(encoding="utf-8"))
        except Exception:
            return []
    return []


def _write(items):
    FILE.write_text(json.dumps(items, indent=2, ensure_ascii=False), encoding="utf-8")


def run(arg: str = "") -> str:
    if not arg:
        return json.dumps({"error": "empty command"}, ensure_ascii=False)
    parts = [p.strip() for p in arg.split("|")]
    cmd = parts[0].lower()
    if cmd == "prepare":
        if len(parts) < 3:
            return json.dumps({"error": "usage: prepare|task_id|profile_name"}, ensure_ascii=False)
        items = _read()
        rec = {"task_id": parts[1], "profile": parts[2], "status": "isolated"}
        items.append(rec)
        _write(items)
        return json.dumps(rec, ensure_ascii=False)
    if cmd == "list":
        return json.dumps(_read(), ensure_ascii=False)
    return json.dumps({"error": "unknown command"}, ensure_ascii=False)
