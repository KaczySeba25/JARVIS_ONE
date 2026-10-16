import os
from openai import OpenAI
from dotenv import load_dotenv, set_key
from pathlib import Path

def run(action="auto"):
    """
    Zarządza modelami AI. 
    Akcje: 
    - 'auto': automatycznie znajduje najlepsze modele i zapisuje je w .env
    - 'list': wypisuje dostępne modele
    """
    load_dotenv(override=True)
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key: return "BŁĄD: Brak GROQ_API_KEY w .env"

    client = OpenAI(api_key=api_key, base_url="https://api.groq.com/openai/v1")
    
    try:
        models_list = client.models.list()
        available_ids = [m.id for m in models_list.data]
        
        if action == "list":
            return "Dostępne modele:\n" + "\n".join(available_ids)

        # LOGIKA WYBORU (Auto-Regulation)
        # Szukamy modelu Qwen dla 'fast' i czegoś dużego dla 'smart'
        fast_model = next((m for m in available_ids if "qwen" in m.lower()), available_ids[0])
        smart_model = next((m for m in available_ids if "120b" in m.lower() or "70b" in m.lower()), available_ids[0])

        # Zapisujemy do pliku .env, aby Jarvis pamiętał to po restarcie
        env_path = Path(".env")
        set_key(str(env_path), "JARVIS_MODEL", fast_model) # Tutaj poprawka na fast_model
        # Uwaga: dla pełnej automatyzacji dodamy też SMART_MODEL do .env
        set_key(str(env_path), "JARVIS_SMART_MODEL", smart_model)
        
        return f"Samo-regulacja zakończona sukcesem!\nUstawiono FAST: {fast_model}\nUstawiono SMART: {smart_model}\nProszę zrestartować agenta."
        
    except Exception as e:
        return f"Błąd podczas regulacji modeli: {str(e)}"
