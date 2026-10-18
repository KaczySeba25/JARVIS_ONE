"""Secure vault for JARVIS ONE.

Stores encrypted secrets in data_vault/vault.json using Fernet (symmetric key) provided
by VAULT_KEY in .env. If VAULT_KEY is missing, vault will raise an error — use
scripts/bootstrap_agent.py to generate one automatically.

API:
 - store_secret(name: str, value: str) -> None
 - get_secret(name: str) -> str | None
 - list_secrets() -> list
"""
import os
import json
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
        raise EnvironmentError("VAULT_KEY not set in environment (.env). Run scripts/bootstrap_agent.py to generate it.")
    return key.encode()


def _load_store() -> dict:
    if VAULT_FILE.exists():
        try:
            return json.loads(VAULT_FILE.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def _write_store(d: dict):
    VAULT_FILE.write_text(json.dumps(d, indent=2, ensure_ascii=False), encoding="utf-8")


def store_secret(name: str, value: str) -> None:
    key = _get_key()
    f = Fernet(key)
    token = f.encrypt(value.encode()).decode()
    store = _load_store()
    store[name] = token
    _write_store(store)


def get_secret(name: str) -> Optional[str]:
    key = _get_key()
    f = Fernet(key)
    store = _load_store()
    token = store.get(name)
    if not token:
        return None
    try:
        return f.decrypt(token.encode()).decode()
    except InvalidToken:
        raise ValueError("Nieprawidłowy VAULT_KEY lub uszkodzony token")


def list_secrets() -> list:
    store = _load_store()
    return list(store.keys())
