"""Email generator skill.

Generuje tymczasowy e-mail i zapisuje go do data_vault/emails.json.
"""
import json
import secrets
import string
from pathlib import Path

DATA_VAULT = Path("data_vault")
DATA_VAULT.mkdir(exist_ok=True)
EMAILS_FILE = DATA_VAULT / "emails.json"


def _random_local(length: int = 12) -> str:
    alphabet = string.ascii_lowercase + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(length))


def _save_email(record: dict):
    items = []
    if EMAILS_FILE.exists():
        try:
            items = json.loads(EMAILS_FILE.read_text(encoding="utf-8"))
        except Exception:
            items = []
    items.append(record)
    EMAILS_FILE.write_text(json.dumps(items, indent=2, ensure_ascii=False), encoding="utf-8")


def run(arg: str = "") -> str:
    email = f"{_random_local()}@1secmail.com"
    record = {"email": email, "domain": "1secmail.com", "created_by": "skills.email_generator"}
    _save_email(record)
    return json.dumps(record, ensure_ascii=False)
