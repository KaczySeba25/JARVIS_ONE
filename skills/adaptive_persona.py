"""Temporal Replay Gadget.

Nagrywa zdarzenia wykonania zadań i pozwala odtwarzać ostatnie replay.
"""
import json
from pathlib import Path

DATA_VAULT = Path("data_vault")
DATA_VAULT.mkdir(exist_ok=True)
FILE = DATA_VAULT / "temporal_replays.json"


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
    if cmd == "record":
        records = _read()
        entry = {"task_id": parts[1] if len(parts) > 1 else "unknown", "event": parts[2] if len(parts) > 2 else "{}"}
        records.append(entry)
        _write(records)
        return json.dumps(entry, ensure_ascii=False)
    if cmd == "list":
        return json.dumps(_read(), ensure_ascii=False)
    if cmd == "latest":
        items = _read()
        return json.dumps(items[-1] if items else {}, ensure_ascii=False)
    return json.dumps({"error": "unknown command"}, ensure_ascii=False)
