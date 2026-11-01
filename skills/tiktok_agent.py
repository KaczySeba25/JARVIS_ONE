"""Skill automatyzujący przygotowanie i tworzenie konta TikTok.

Funkcjonalność:
- Gdy wywołasz `run("otworz konto na tiktoku")`, skill:
  1. Wygeneruje tymczasowy adres e-mail oparty na 1secmail.com (public API), oraz silne hasło.
  2. Zapisze poświadczenia w `data_vault/tiktok_accounts.json` (append).
  3. Utworzy skrypt automatyzujący tworzenie konta w `scripts/create_tiktok_account_playwright.py`.
  4. Zwróci instrukcje i informacje do natychmiastowego uruchomienia.

Uwaga bezpieczeństwa:
- Ten skrypt tworzy lokalne zapisy poświadczeń; zadbaj o ich bezpieczne przechowywanie.
- Do pełnej automatyzacji wymagany jest Playwright (pakiet Python) oraz zainstalowane przeglądarki (uruchom: `playwright install`).
- Tworzenie kont może naruszać regulamin usług; używaj odpowiedzialnie.
"""

import os
import json
import secrets
import string
from pathlib import Path

DATA_VAULT = Path("data_vault")
DATA_VAULT.mkdir(exist_ok=True)
ACCOUNTS_FILE = DATA_VAULT / "tiktok_accounts.json"
SCRIPTS_DIR = Path("scripts")
SCRIPTS_DIR.mkdir(exist_ok=True)


def _random_username(prefix="jarvis", length=6):
    suf = ''.join(secrets.choice(string.ascii_lowercase + string.digits) for _ in range(length))
    return f"{prefix}{suf}"


def _random_password(length=14):
    alphabet = string.ascii_letters + string.digits + string.punctuation
    return ''.join(secrets.choice(alphabet) for _ in range(length))


def _save_account(record: dict):
    existing = []
    if ACCOUNTS_FILE.exists():
        try:
            existing = json.loads(ACCOUNTS_FILE.read_text(encoding="utf-8"))
        except Exception:
            existing = []
    existing.append(record)
    ACCOUNTS_FILE.write_text(json.dumps(existing, indent=2, ensure_ascii=False), encoding="utf-8")


def _write_playwright_script(path: Path):
    content = """#!/usr/bin/env python3
"""Automatyczny skrypt Playwright do tworzenia konta TikTok.

Uruchom: python scripts/create_tiktok_account_playwright.py --email <email> --password <password>

Skrypt:
- otwiera stronę TikTok
- wybiera rejestrację przez e-mail (w zależności od UI)
- wypełnia formularz e-mail + hasło
- czeka na wiadomość w 1secmail API i wklepuje kod weryfikacyjny

Uwaga: UI TikTok się zmienia; możliwe, że konieczne będzie dostosowanie selektorów.
"""
from playwright.sync_api import sync_playwright
import time
import requests
import argparse

API_1SEC = "https://www.1secmail.com/api/v1/"


def poll_verification(username, domain, timeout=180, interval=5):
    end = time.time() + timeout
    while time.time() < end:
        try:
            r = requests.get(API_1SEC, params={"action": "getMessages", "login": username, "domain": domain}, timeout=15)
            msgs = r.json()
            if msgs:
                # pobierz pierwszą wiadomość
                msg_id = msgs[0]["id"]
                r2 = requests.get(API_1SEC, params={"action": "readMessage", "login": username, "domain": domain, "id": msg_id}, timeout=15)
                data = r2.json()
                body = data.get("body", "")
                # prosta ekstrakcja kodu (6 cyfr)
                import re
                m = re.search(r"(\d{4,8})", body)
                if m:
                    return m.group(1)
        except Exception:
            pass
        time.sleep(interval)
    return None


def main(email, password):
    # email = localpart@domain
    local, domain = email.split("@", 1)
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto("https://www.tiktok.com")
        time.sleep(2)
        # Przykładowe kroki - mogą wymagać adaptacji
        try:
            # Otwórz modal rejestracji
            page.click('button:has-text("Zaloguj się")')
            time.sleep(1)
        except Exception:
            pass
        try:
            page.click('button:has-text("Zarejestruj się")')
            time.sleep(1)
        except Exception:
            pass
        # Znajdź opcję mail
        # UWAGA: selektory mogą być różne; dostosuj je jeśli skrypt się nie wykonuje
        try:
            page.click('text="Użyj e-maila"')
        except Exception:
            try:
                page.click('text="Use phone or email"')
            except Exception:
                pass
        time.sleep(1)
        # Wypełnij e-mail i hasło
        try:
            page.fill('input[type="email"]', email)
        except Exception:
            pass
        try:
            page.fill('input[type="password"]', password)
        except Exception:
            pass
        # Wyślij formularz
        try:
            page.click('button:has-text("Dalej")')
        except Exception:
            pass

        # Poll 1secmail for verification code
        code = poll_verification(local, domain, timeout=180, interval=5)
        if code:
            # Wklej kod w pole
            try:
                page.fill('input[type="tel"]', code)
            except Exception:
                pass
        else:
            print("Nie otrzymano kodu weryfikacyjnego w czasie oczekiwania. Sprawdź ręcznie.")

        print("Zakończono próbę rejestracji. Sprawdź stronę przeglądarki i ewentualne komunikaty.")
        browser.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--email', required=True)
    parser.add_argument('--password', required=True)
    args = parser.parse_args()
    main(args.email, args.password)
"""
    path.write_text(content, encoding="utf-8")
    try:
        path.chmod(0o755)
    except Exception:
        pass


def run(query: str = "") -> str:
    """Punkt wejścia dla skillu.

    Jeśli `query` zawiera słowa kluczowe dotyczące tworzenia konta TikTok,
    skill automatycznie przygotuje e-mail, hasło, zapisze dane i wygeneruje skrypt automatyzacji.
    """
    if not query:
        return 'Użycie: run("otworz konto na tiktoku")'

    q = query.lower()
    if "tiktok" not in q:
        return 'Ten skill obsługuje tylko TikTok. Wywołaj go z: "otworz konto na tiktoku"'

    username = _random_username()
    domain = "1secmail.com"
    email = f"{username}@{domain}"
    password = _random_password()

    record = {
        "email": email,
        "username": username,
        "password": password,
        "notes": "Utworzone przez skills/tiktok_agent.py"
    }

    _save_account(record)

    # Utwórz skrypt Playwright
    script_path = SCRIPTS_DIR / "create_tiktok_account_playwright.py"
    _write_playwright_script(script_path)

    return (
        f"Przygotowano dane do rejestracji TikTok:\n"
        f" - e-mail: {email}\n"
        f" - hasło: {password}\n"
        f"Dane zapisano w: {ACCOUNTS_FILE}\n"
        f"Skrypt automatyzacji: {script_path}\n"
        f"Aby wykonać automatyzację:\n"
        f" 1) Upewnij się, że masz zainstalowane zależności: python scripts/bootstrap_agent.py\n"
        f" 2) Zainstaluj przeglądarki Playwright: playwright install\n"
        f" 3) Uruchom: python {script_path} --email {email} --password {password}\n"
        f"Jeśli chcesz, mogę spróbować uruchomić skrypt automatycznie (wymaga zgody na uruchamianie przeglądarki)."
    )
