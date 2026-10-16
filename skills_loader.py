import importlib
from pathlib import Path

SKILLS_DIR = Path("skills")

def get_skills_manifest():
    """Dynamicznie przeszukuje folder skills/ i pobiera opisy wszystkich umiejętności."""
    manifest = []
    if not SKILLS_DIR.exists():
        return "Brak katalogu skills."

    for file in SKILLS_DIR.glob("*.py"):
        if file.name.startswith("_"):
            continue
        skill_name = file.stem
        try:
            module = importlib.import_module(f"skills.{skill_name}")
            importlib.reload(module)
            doc = module.__doc__.strip() if module.__doc__ else "Brak opisu skilla."
            manifest.append(f"- [{skill_name}]: {doc}")
        except Exception as e:
            manifest.append(f"- [{skill_name}]: Błąd ładowania opisu ({e})")

    return "\n".join(manifest) if manifest else "Brak zarejestrowanych skilli."

def execute_skill(skill_name):
    """Dynamicznie importuje, przeładowuje i uruchamia zadaną umiejętność."""
    skill_path = SKILLS_DIR / f"{skill_name}.py"
    if not skill_path.exists():
        raise FileNotFoundError(f"Skill '{skill_name}' nie istnieje.")

    module_name = f"skills.{skill_name}"
    module = importlib.import_module(module_name)
    importlib.reload(module)  # <--- Kluczowa linijka: wymusza odczyt najnowszego kodu z dysku

    if hasattr(module, 'run'):
        return module.run()
    else:
        raise AttributeError(f"Skill '{skill_name}' nie posiada wymaganej funkcji run().")
