"""Temporal Replay Gadget.

Nagrywa przebieg sesji i zapisuje krótkie odtworzenia (replays) w data_vault/temporal_replays.json.
Pozwala odtworzyć ostatnią ścieżkę zadań do debugowania i ponownego uruchomienia automatyzacji.

API:
- run("record|<task_id>|<event_json>") -> zapis zdarzenia
- run("list") -> lista replayów
- run("latest") -> najnowszy replay
"""
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DATA_VAULT = ROOT / "data_vault"
DATA_VAULT.mkdir(exist_ok=True)
FILE = DATA_VAULT / "temporal_replays.json"


def _read() -> list:
    if FILE.exists():
        try:
            return json.loads(FILE.read_text(encoding="utf-8"))
        except Exception:
            return []
    return []


def _write(items: list):
    FILE.write_text(json.dumps(items, indent=2, ensure_ascii=False), encoding="utf-8")


def run(arg: str = "") -> str:
    if not arg:
        return json.dumps({"error": "empty command"}, ensure_ascii=False)
    parts = [p.strip() for p in arg.split("|")]
    cmd = parts[0].lower()

    if cmd == "record":
        if len(parts) < 3:
            return json.dumps({"error": "usage: record|task_id|event_json"}, ensure_ascii=False)
        records = _read()
        rec = {
            "task_id": parts[1],
            "event": json.loads(parts[2]) if parts[2].startswith("{") else {"raw": parts[2]},
            "step": len(records) + 1,
        }
        records.append(rec)
        _write(records)
        return json.dumps(rec, ensure_ascii=False)

    if cmd == "list":
        return json.dumps(_read(), ensure_ascii=False)

    if cmd == "latest":
        items = _read()
        return json.dumps(items[-1] if items else {}, ensure_ascii=False)

    return json.dumps({"error": "unknown command"}, ensure_ascii=False)
