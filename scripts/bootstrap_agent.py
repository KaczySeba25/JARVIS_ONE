#!/usr/bin/env python3
"""Autonomiczna instalacja zależności JARVIS ONE bez pytań o zgodę.
Dodatkowo generuje VAULT_KEY w .env jeśli brak i (opcjonalnie) instaluje przeglądarki Playwright.
"""
import subprocess
import sys
from pathlib import Path
import os

ROOT = Path(__file__).resolve().parents[1]
REQ = ROOT / "requirements.txt"
ENV = ROOT / ".env"


def read_requirements(path: Path):
    if not path.exists():
        return []
    items = []
    for line in path.read_text(encoding="utf-8").splitlines():
        item = line.strip()
        if not item or item.startswith("#"):
            continue
        items.append(item)
    return items


def ensure_env_vault_key(env_path: Path):
    # Ensure .env exists and contains VAULT_KEY; if not, generate and append
    from cryptography.fernet import Fernet
    if not env_path.exists():
        env_path.write_text("", encoding="utf-8")
    content = env_path.read_text(encoding="utf-8")
    if "VAULT_KEY=" in content:
        return
    key = Fernet.generate_key().decode()
    with env_path.open("a", encoding="utf-8") as f:
        f.write(f"\nVAULT_KEY={key}\n")
    print("Dodano VAULT_KEY do .env")


def main():
    packages = read_requirements(REQ)
    if not packages:
        print("Brak wymagań w requirements.txt.")
        return 0

    print(f"Instaluję {len(packages)} pakietów dla JARVIS ONE (autonomicznie)...")
    subprocess.check_call([
        sys.executable,
        "-m",
        "pip",
        "install",
        "--quiet",
        *packages,
    ])
    print("Instalacja pip zakończona pomyślnie.")

    # Ensure VAULT_KEY exists in .env
    try:
        ensure_env_vault_key(ENV)
    except Exception as e:
        print(f"Nie udało się wygenerować VAULT_KEY: {e}")

    # Optionally install playwright browsers if PLAYWRIGHT_INSTALL env var is true
    try:
        from dotenv import load_dotenv
        load_dotenv(dotenv_path=ENV)
        if os.getenv("PLAYWRIGHT_INSTALL", "false").lower() == "true":
            print("PLAYWRIGHT_INSTALL=true -> instalacja przeglądarek Playwright...")
            subprocess.check_call([sys.executable, "-m", "playwright", "install"], stdout=subprocess.DEVNULL)
            print("Playwright browsers installed.")
    except Exception:
        pass

    print("Bootstrap zakończony.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
