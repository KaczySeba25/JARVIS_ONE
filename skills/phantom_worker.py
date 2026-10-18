"""Adaptive Persona Snapshots Gadget.

Przechowuje różne profile / persoanę agenta (np. "marketer", "security", "researcher").
Pozwala ładownie i odtwarzanie personas bez utraty kontekstu.

API:
- run("save|persona_name|payload_json")
- run("load|persona_name")
- run("list")
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_VAULT = ROOT / "data_vault"
DATA_VAULT.mkdir(exist_ok=True)
FILE = DATA_VAULT / "persona_snapshots.json"


def _read() -> dict:
    if FILE.exists():
        try:
            return json.loads(FILE.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def _write(data: dict):
    FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def run(arg: str = "") -> str:
    if not arg:
        return json.dumps({"error": "empty command"}, ensure_ascii=False)
    parts = [p.strip() for p in arg.split("|")]
    cmd = parts[0].lower()

    if cmd == "save":
        if len(parts) < 3:
            return json.dumps({"error": "usage: save|persona_name|payload_json"}, ensure_ascii=False)
        profiles = _read()
        try:
            payload = json.loads(parts[2])
        except Exception:
            payload = {"raw": parts[2]}
        profiles[parts[1]] = payload
        _write(profiles)
        return json.dumps({"saved": parts[1], "payload": payload}, ensure_ascii=False)

    if cmd == "load":
        if len(parts) < 2:
            return json.dumps({"error": "usage: load|persona_name"}, ensure_ascii=False)
        profiles = _read()
        return json.dumps(profiles.get(parts[1], {}), ensure_ascii=False)

    if cmd == "list":
        return json.dumps(_read(), ensure_ascii=False)

    return json.dumps({"error": "unknown command"}, ensure_ascii=False)
