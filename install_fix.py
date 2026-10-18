#!/usr/bin/env python3
"""Autonomiczna instalacja zależności JARVIS ONE bez pytań o zgodę."""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQ = ROOT / "requirements.txt"


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


def main():
    packages = read_requirements(REQ)
    if not packages:
        print("Brak wymagań w requirements.txt.")
        return 0

    print(f"Instaluję {len(packages)} pakietów dla JARVIS ONE...")
    subprocess.check_call([
        sys.executable,
        "-m",
        "pip",
        "install",
        "--quiet",
        *packages,
    ])
    print("Instalacja zakończona pomyślnie.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
