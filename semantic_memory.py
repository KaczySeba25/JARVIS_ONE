"""
Prosty moduł pamięci semantycznej oparty na pliku JSON.
Funkcje wymagane przez agent.py:
- get_all_memories() -> lista pamięci (ostatnie pierwsze)
- save_memory(category, key, content) -> zwraca zapisany obiekt
- search_memory(query) -> lista wyników (słabe dopasowanie substring)

Uwaga: pliki zapisywane są w katalogu data_vault/ (który powinien być w .gitignore).
"""

import os
import json
from pathlib import Path

DATA_DIR = Path("data_vault")
DATA_DIR.mkdir(parents=True, exist_ok=True)
MEM_FILE = DATA_DIR / "memory.json"

def _load():
    if not MEM_FILE.exists():
        return []
    try:
        with MEM_FILE.open("r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []

def _save(all_mem):
    with MEM_FILE.open("w", encoding="utf-8") as f:
        json.dump(all_mem, f, ensure_ascii=False, indent=2)

def get_all_memories():
    """Zwraca listę pamięci (najnowsze na końcu)."""
    return _load()

def save_memory(category, key, content):
    """Zapisuje pamięć i zwraca obiekt."""
    all_mem = _load()
    item = {
        "category": category,
        "key": key,
        "content": content,
    }
    all_mem.append(item)
    _save(all_mem)
    return item

def search_memory(query):
    """Proste wyszukiwanie - zwraca listę pasujących elementów.
    Używa case-insensitive substring matchów na polu content i key.
    """
    q = str(query).lower()
    results = []
    for m in _load():
        if q in str(m.get("content","")).lower() or q in str(m.get("key","")).lower():
            results.append(m)
    return results
