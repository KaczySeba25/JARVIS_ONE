"""
Skill: self_awareness
Opis: Modul samoświadomości Jarvisa. Pozwala mu poznac wlasne mozliwosci,
ograniczenia, historie i bledy. Nie zgaduje - czyta wlasny kod i dane.
Funkcje: who_am_i, get_my_capabilities, get_my_limitations,
         get_my_history, get_my_mistakes, check_plan, reflect, report.
"""
import os
import sys
import json
from pathlib import Path

HERE = Path(__file__).parent
ROOT = HERE.parent
SKILLS_DIR = HERE
AGENT_FILE = ROOT / "agent.py"
VAULT_DIR = ROOT / "data_vault"
LESSONS_FILE = VAULT_DIR / "error_lessons.json"

# dodaj sciezke do semantic_memory
sys.path.insert(0, str(SKILLS_DIR))


def get_my_capabilities() -> list:
    """Lista skilli z ich opisami z docstringow."""
    caps = []
    for f in sorted(SKILLS_DIR.glob("*.py")):
        if f.name.startswith("_") or f.name == "self_awareness.py":
            continue
        try:
            text = f.read_text(encoding="utf-8")
            lines = text.split("\n")
            desc = "brak opisu"
            # szukaj pierwszego docstringa
            in_doc = False
            doc_lines = []
            for line in lines[:30]:
                s = line.strip()
                if s.startswith('"""') or s.startswith("'''"):
                    if in_doc:
                        break
                    in_doc = True
                    inner = s.strip('"').strip("'").strip()
                    if inner:
                        doc_lines.append(inner)
                    continue
                if in_doc:
                    if s.startswith('"""') or s.startswith("'''"):
                        break
                    doc_lines.append(s)
            if doc_lines:
                desc = " ".join(doc_lines)[:200]
            caps.append({"skill": f.stem, "opis": desc})
        except Exception as e:
            caps.append({"skill": f.stem, "opis": "blad odczytu: " + str(e)})
    return caps


def get_my_limitations() -> list:
    """Rzeczy ktorych Jarvis NIE potrafi (na podstawie brakow)."""
    lims = []
    caps = [c["skill"] for c in get_my_capabilities()]

    if "trading_agent" not in caps:
        lims.append("Brak dzialajacego agenta tradingowego")
    if "notification" not in caps:
        lims.append("Brak systemu powiadomien (email/SMS)")
    if "scheduler" not in caps:
        lims.append("Brak schedulera (24/7 wymaga GitHub Actions / VPS)")
    if "backup" not in caps:
        lims.append("Brak automatycznego backupu danych")
    if "monitoring" not in caps:
        lims.append("Brak monitoringu bledow w czasie rzeczywistym")

    # realne ograniczenia architektury
    lims.append("Pamiec rozmowy nie trwa miedzy sesjami (tylko skills i semantic_memory)")
    lims.append("Nie mam dostepu do prywatnych API bez klucza w vaultcie")
    lims.append("Dzialam na Codespace ktory usypia po 30 min bezczynnosci")

    return lims


def get_my_history() -> str:
    """Ostatnie zadania z semantic_memory."""
    try:
        import semantic_memory as sm
        mems = sm.get_all_memories()
        if not mems:
            return "Brak historii."
        lines = []
        for m in mems[-10:]:
            cat = m.get("category", "?")
            key = m.get("key", "?")
            content = (m.get("content", "") or "")[:150]
            ts = (m.get("timestamp", "") or "")[:19]
            lines.append("- [" + ts + "] (" + cat + "/" + key + "): " + content)
        return "\n".join(lines)
    except Exception as e:
        return "Blad odczytu historii: " + str(e)


def get_my_mistakes() -> list:
    """Bledy z error_lessons.json."""
    if not LESSONS_FILE.exists():
        return []
    try:
        data = json.loads(LESSONS_FILE.read_text(encoding="utf-8"))
        return data[-10:]  # ostatnie 10
    except Exception:
        return []


def who_am_i() -> str:
    """
    Introspekcja: kim jestem, co potrafie, ile sie nauczylem.
    Nie zgaduje - czyta wlasny kod i dane.
    """
    caps = get_my_capabilities()
    lims = get_my_limitations()
    mistakes = get_my_mistakes()

    # policz wspomnienia
    mem_count = 0
    try:
        import semantic_memory as sm
        mem_count = len(sm.get_all_memories())
    except Exception:
        pass

    # policz pliki w agents/
    agents_dir = ROOT / "agents"
    agent_dirs = []
    if agents_dir.exists():
        for d in agents_dir.iterdir():
            if d.is_dir() and not d.name.startswith("__"):
                agent_dirs.append(d.name)

    lines = [
        "=== KIM JESTEM ===",
        "Nazywam sie JARVIS ONE.",
        "Jestem autonomicznym agentem AI zbudowanym przez Sebastiana Kaczora.",
        "Dzialam w /workspaces/JARVIS_ONE (GitHub Codespaces).",
        "",
        "=== MOJE MOZLIWOSCI (" + str(len(caps)) + " skilli) ===",
    ]
    for c in caps:
        lines.append("  - " + c["skill"] + ": " + c["opis"][:120])

    lines.append("")
    lines.append("=== MOJE OGRANICZENIA ===")
    for l in lims:
        lines.append("  - " + l)

    lines.append("")
    lines.append("=== MOJA PAMIEC ===")
    lines.append("  Wspomnien w semantic_memory: " + str(mem_count))
    lines.append("  Lekcji z bledow: " + str(len(mistakes)))

    lines.append("")
    lines.append("=== MOJE SUB-AGENTY ===")
    if agent_dirs:
        for a in agent_dirs:
            lines.append("  - " + a)
    else:
        lines.append("  (brak)")

    lines.append("")
    lines.append("=== OSTATNIE ZADANIA ===")
    lines.append(get_my_history())

    return "\n".join(lines)


def check_plan(plan: str) -> dict:
    """
    Waliduje plan przed wykonaniem.
    Zwraca {ok: bool, warnings: [...], suggestions: [...]}.
    """
    warnings = []
    suggestions = []
    low = plan.lower()

    # 1. Prawdziwe pieniadze
    dangerous = ["prawdziwe pieniadze", "live trading", "api.binance.com",
                 "produkcja", "real money", "przelew", "bank"]
    for d in dangerous:
        if d in low:
            warnings.append("UWAGA: plan zawiera '" + d + "' - wymaga potwierdzenia Sebastiana.")

    # 2. Powtarzanie znanych bledow
    mistakes = get_my_mistakes()
    for m in mistakes:
        err = m.get("error_message", "")[:60]
        if err and err.lower() in low:
            warnings.append("Plan powtarza znany blad: " + err)

    # 3. Czy plan jest kompletny
    if len(plan) < 100:
        suggestions.append("Plan jest krotki - rozwaz dodanie szczegolow.")
    if "test" not in low and "weryfik" not in low:
        suggestions.append("Brak kroku testowania/weryfikacji.")

    # 4. Czy zaplanowano research
    if "research" not in low and "zbadaj" not in low and "sprawdz" not in low:
        suggestions.append("Brak kroku research - rozwaz [FETCH_URL] przed budowa.")

    return {
        "ok": len(warnings) == 0,
        "warnings": warnings,
        "suggestions": suggestions,
    }


def reflect(task: str, outcome: str, lessons: str) -> str:
    """
    Zapisuje refleksje po zadaniu. Wywoluj na koniec kazdego zadania.
    """
    try:
        import semantic_memory as sm
        key = "refleksja_" + task[:40].replace(" ", "_")
        content = "ZADANIE: " + task + "\nWYNIK: " + outcome + "\nLEKCJE: " + lessons
        return sm.save_memory("refleksje", key, content)
    except Exception as e:
        return "Blad zapisu refleksji: " + str(e)


def report() -> str:
    """Pelen raport o sobie dla Sebastiana."""
    return who_am_i()


def run():
    """Domyslne uruchomienie - pokazuje kim jestem."""
    return who_am_i()


if __name__ == "__main__":
    print(run())