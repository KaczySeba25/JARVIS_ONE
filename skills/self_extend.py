"""Skill: self_extend - autonomiczne tworzenie nowych skilli."""
import os
import py_compile as _pc

SKILLS_DIR = "skills"


def create(skill_name, description, code=None):
    """Tworzy nowy skill. Jesli code=None, uzywa szablonu."""
    skill_name = skill_name.strip().replace(".py", "")
    if not skill_name.replace("_", "").isalnum():
        return "BLAD: nazwa '" + skill_name + "' nieprawidlowa."
    path = os.path.join(SKILLS_DIR, skill_name + ".py")
    if os.path.exists(path):
        return "BLAD: skill '" + skill_name + "' juz istnieje."
    TQ = '"' * 3
    if code is None:
        code = TQ + description + TQ + "\n\n\ndef run():\n    return \"" + description + " - szkielet\"\n"
    if not code.lstrip().startswith(TQ):
        return "BLAD: brak docstringa."
    if "def run(" not in code:
        return "BLAD: brak funkcji run()."
    with open(path, "w", encoding="utf-8") as f:
        f.write(code)
    try:
        _pc.compile(path, doraise=True)
    except _pc.PyCompileError as e:
        os.remove(path)
        return "BLAD skladni:\n" + str(e)
    return "OK: stworzono " + path


def run():
    return "self_extend gotowy."
