"""
Prosty manager sejfu (vault). Zapisuje dane do pliku JSON w katalogu data_vault/.
UWAGA: To NIE jest bezpieczny, kryptograficzny sejf. Plik data_vault/ powinien być w .gitignore
(i wg repo już jest). Ten moduł daje wygodny interfejs do zapisu/odczytu danych dostępowych
używanych przez Jarvisa podczas testów lokalnych.

Funkcje:
- save_credentials(name, mapping) -> zapisuje (nadpisuje) dane pod nazwą
- get_credentials(name) -> zwraca zapisane dane lub None
- list_credentials() -> lista nazw
"""

import os
import json
from pathlib import Path

DATA_DIR = Path("data_vault")
DATA_DIR.mkdir(parents=True, exist_ok=True)
VAULT_FILE = DATA_DIR / "vault.json"

def _load():
    if not VAULT_FILE.exists():
        return {}
    try:
        with VAULT_FILE.open("r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def _save(d):
    with VAULT_FILE.open("w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=2)

def save_credentials(name, mapping):
    d = _load()
    d[name] = mapping
    _save(d)
    return True

def get_credentials(name):
    return _load().get(name)

def list_credentials():
    return list(_load().keys())
