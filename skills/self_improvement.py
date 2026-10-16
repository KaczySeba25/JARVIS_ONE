"""
Skill: self_improvement
Opis: Produkcyjny moduł kontroli jakości, testowania i nauki na błędach oraz optymalizacji logiki.
"""
import sys
import json
import traceback
import subprocess
from pathlib import Path
from datetime import datetime

VAULT_DIR = Path("data_vault")
LESSONS_FILE = VAULT_DIR / "error_lessons.json"
OPTIMIZATION_FILE = VAULT_DIR / "logic_optimizations.json"

def _load_json(file_path):
    VAULT_DIR.mkdir(parents=True, exist_ok=True)
    if not file_path.exists(): return []
    try: return json.loads(file_path.read_text(encoding="utf-8"))
    except Exception: return []

def _save_json(file_path, data):
    VAULT_DIR.mkdir(parents=True, exist_ok=True)
    file_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

def log_error_lesson(context: str, error_msg: str, trace: str = "") -> str:
    lessons = _load_json(LESSONS_FILE)
    lesson_entry = {
        "timestamp": datetime.now().isoformat(),
        "context": context,
        "error_message": error_msg,
        "traceback": trace,
        "status": "ANALYZED"
    }
    lessons.append(lesson_entry)
    _save_json(LESSONS_FILE, lessons)
    return f"Lekcja błędu zarejestrowana dla '{context}'."

def save_optimization_tip(logic_path: str, tip: str) -> str:
    """Zapisuje lekcję o tym, jak zrobić coś szybciej/lepiej."""
    tips = _load_json(OPTIMIZATION_FILE)
    entry = {
        "timestamp": datetime.now().isoformat(),
        "path": logic_path,
        "tip": tip
    }
    tips.append(entry)
    _save_json(OPTIMIZATION_FILE, tips)
    return f"Lekcja optymalizacji zapisana dla ścieżki: {logic_path}"

def test_sub_agent(agent_path: str) -> str:
    if not agent_path.endswith(".py"): return "BLAD: Musi być .py"
    if not Path(agent_path).exists(): return f"BLAD: {agent_path} nie istnieje."
    try:
        result = subprocess.run([sys.executable, agent_path], capture_output=True, text=True, timeout=15)
        if result.returncode == 0:
            return f"SUKCES: {agent_path} działa.\nWynik:\n{result.stdout}"
        else:
            error_msg = result.stderr or result.stdout
            log_error_lesson(f"sub_agent_run:{agent_path}", error_msg)
            return f"BŁĄD URUCHOMIENIA {agent_path}:\n{error_msg}"
    except Exception as e: return f"BŁĄD SYSTEMOWY: {str(e)}"

def run() -> str:
    lessons = _load_json(LESSONS_FILE)
    opts = _load_json(OPTIMIZATION_FILE)
    return f"=== SELF IMPROVEMENT DEBUGGER ===\nLekcje błędów: {len(lessons)}\nLekcje optymalizacji: {len(opts)}\nStatus: OPERACYJNY"

if __name__ == "__main__":
    print(run())

