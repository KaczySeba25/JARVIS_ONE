"""
Skill: agent_registry
Opis: Zarządza rejestrem sub-agentów. Pozwala dodawać, usuwać i listować agenty w katalogu /agents.
"""
import os
import json

REGISTRY_PATH = "agents/registry.json"

def _load_registry():
    if not os.path.exists(REGISTRY_PATH):
        return {}
    try:
        with open(REGISTRY_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def _save_registry(data):
    os.makedirs("agents", exist_ok=True)
    with open(REGISTRY_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

def run():
    """
    Uruchamia rejestr. Oczekuje na polecenie w formie:
    - 'list' -> lista wszystkich agentów
    - 'add | nazwa | opis | wersja' -> dodaje agenta
    - 'remove | nazwa' -> usuwa agenta
    """
    # Ponieważ skills_loader wywołuje run() bez argumentów, 
    # ten skill jest przeznaczony do pracy przez Jarvisa, który 
    # może go rozbudować lub użyć do analizy registry.json
    
    registry = _load_registry()
    if not registry:
        return "Rejestr jest pusty. Użyj [WRITE_FILE] aby stworzyć registry.json lub poproś o dodanie agenta."
    
    output = "=== REJESTR SUB-AGENTÓW ===\n"
    for name, info in registry.items():
        output += f"- {name}: {info.get('desc', 'Brak opisu')} (v{info.get('ver', '1.0')})\n"
    
    return output
