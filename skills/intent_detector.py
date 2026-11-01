"""Secure vault for JARVIS ONE.

Stores encrypted secrets in data_vault/vault.json using Fernet.
"""
import json
import os
from pathlib import Path
from typing import Optional

from cryptography.fernet import Fernet, InvalidToken

ROOT = Path(__file__).resolve().parents[1]
DATA_VAULT = ROOT / "data_vault"
DATA_VAULT.mkdir(exist_ok=True)
VAULT_FILE = DATA_VAULT / "vault.json"


def _get_key() -> bytes:
    key = os.getenv("VAULT_KEY")
    if not key:
        raise EnvironmentError("VAULT_KEY nie ustawione. Uruchom python scripts/bootstrap_agent.py.")
    return key.encode()


def _load_store() -> dict:
    if not VAULT_FILE.exists():
        return {}
    try:
        return json.loads(VAULT_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _write_store(data: dict):
    VAULT_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def store_secret(name: str, value: str) -> None:
    f = Fernet(_get_key())
    token = f.encrypt(value.encode("utf-8")).decode("utf-8")
    store = _load_store()
    store[name] = token
    _write_store(store)


def get_secret(name: str) -> Optional[str]:
    f = Fernet(_get_key())
    store = _load_store()
    token = store.get(name)
    if not token:
        return None
    try:
        return f.decrypt(token.encode("utf-8")).decode("utf-8")
    except InvalidToken as exc:
        raise ValueError("Nieprawidłowy VAULT_KEY lub uszkodzony token") from exc


def list_secrets() -> list:
    return list(_load_store().keys())
