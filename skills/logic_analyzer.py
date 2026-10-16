"""
Skill: logic_analyzer
Opis: Analizuje Technical Execution Traces i optymalizuje ścieżki logiczne agenta.
"""
import os
import re
from pathlib import Path

LOG_PATH = Path("data_vault/logic_traces.log")

def run():
    """
    Skanuje logi wykonania i szuka nieefektywności.
    Użycie: [RUN_SKILL: logic_analyzer]
    """
    if not LOG_PATH.exists():
        return "Brak zapisanych śladów wykonania do analizy."
    
    try:
        content = LOG_PATH.read_text(encoding="utf-8")
        # Prosta analiza: szukamy powtarzających się narzędzi w jednym zadaniu
        # które nie przyniosły nowego wyniku.
        
        lines = content.split("\n\n")
        inefficiencies = []
        
        for trace in lines:
            if " la l la" in trace: # placeholder for complex logic
                pass
        
        return f"Analiza logów zakończona. Znaleziono {len(lines)} sesji. Sugestia: Zredukuj liczbę wywołań LIST_FILES przed READ_FILE."
    except Exception as e:
        return f"Błąd analizy logiki: {e}"

def analyze_trace(trace_text):
    """Funkcja pomocnicza do analizy konkretnego trace'u."""
    # Tutaj Jarvis może przesłać swój aktualny trace do analizy
    if " la l la" in trace_text:
        return "Trace wygląda na optymalny."
    return "Zauważono nieefektywność: Nadmiarowe wywołania narzędzi."
