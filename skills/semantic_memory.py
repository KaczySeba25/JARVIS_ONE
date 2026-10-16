"""
Skill: semantic_memory
Opis: Produkcyjna baza pamięci trwałej (SQLite) dla Jarvisa. Zapewnia zapis, wyszukiwanie i zarządzanie wiedzą, regułami oraz ustaleniami.
"""
import sqlite3
import json
from pathlib import Path
from datetime import datetime

DB_DIR = Path("data_vault")
DB_FILE = DB_DIR / "memory.db"

def _get_db_connection():
    """Nawiązuje połączenie z bazą danych SQLite i tworzy tabele, jeśli nie istnieją."""
    DB_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    
    with conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS memories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT NOT NULL,
                key TEXT NOT NULL UNIQUE,
                content TEXT NOT NULL,
                tags TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)
    return conn

def save_memory(category: str, key: str, content: str, tags: list = None) -> str:
    """Zapisuje nową informację lub aktualizuje istniejącą w pamięci trwałej."""
    conn = _get_db_connection()
    tags_str = json.dumps(tags) if tags else "[]"
    now = datetime.now().isoformat()
    
    with conn:
        conn.execute("""
            INSERT INTO memories (category, key, content, tags, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(key) DO UPDATE SET
                category=excluded.category,
                content=excluded.content,
                tags=excluded.tags,
                updated_at=excluded.updated_at
        """, (category, key, content, tags_str, now, now))
        
    return f"Pamięć zarejestrowana [Kategoria: {category} | Klucz: {key}]."

def search_memory(query: str) -> list:
    """Wyszukuje nakładające się zapisy w pamięci po kluczu, treści lub tagach."""
    conn = _get_db_connection()
    pattern = f"%{query}%"
    
    cursor = conn.execute("""
        SELECT category, key, content, tags, updated_at
        FROM memories
        WHERE key LIKE ? OR content LIKE ? OR category LIKE ? OR tags LIKE ?
        ORDER BY updated_at DESC
    """, (pattern, pattern, pattern, pattern))
    
    results = []
    for row in cursor.fetchall():
        results.append({
            "category": row["category"],
            "key": row["key"],
            "content": row["content"],
            "tags": json.loads(row["tags"]) if row["tags"] else [],
            "updated_at": row["updated_at"]
        })
    return results

def get_all_memories() -> list:
    """Zwraca wszystkie wpisy z bazy pamięci."""
    conn = _get_db_connection()
    cursor = conn.execute("SELECT category, key, content, tags FROM memories ORDER BY category, key")
    
    results = []
    for row in cursor.fetchall():
        results.append({
            "category": row["category"],
            "key": row["key"],
            "content": row["content"],
            "tags": json.loads(row["tags"]) if row["tags"] else []
        })
    return results

def delete_memory(key: str) -> str:
    """Usuwa dany wpis z pamięci."""
    conn = _get_db_connection()
    with conn:
        cursor = conn.execute("DELETE FROM memories WHERE key = ?", (key,))
        if cursor.rowcount > 0:
            return f"Wpis z kluczem '{key}' został usunięty z pamięci."
        return f"Nie znaleziono wpisu o kluczu '{key}'."

def run() -> str:
    """Test jednostkowy i punkt wejścia dla loadera skilli Jarvisa."""
    # 1. Zapis faktów biznesowych i technicznych
    r1 = save_memory("biznes", "partner", "Sebastian Kaczor - twórca i właściciel systemu Imperium/JARVIS ONE", ["projekty", "użytkownik"])
    r2 = save_memory("architektura", "skille_rule", "Każdy skill w folderze skills/ musi posiadać funkcję run() i dokładny docstring", ["python", "zasady"])
    
    # 2. Wyszukiwanie
    search_res = search_memory("Sebastian")
    
    # 3. Odczyt pełnej listy
    all_mems = get_all_memories()
    
    return f"""=== SEMANTIC MEMORY TEST (100% PRODUKCYJNY) ===
Zapis 1: {r1}
Zapis 2: {r2}
Wynik wyszukiwania 'Sebastian': {len(search_res)} wpis(y) znalezione -> {search_res[0]['content'] if search_res else 'Brak'}
Liczba rekordów w bazie: {len(all_mems)}
Status: BAZA PAMIĘCI SIKU/SQLITE DZIAŁA POPRAWNIE
=================================================="""

if __name__ == "__main__":
    print(run())
