# Protokół Pozyskiwania i Weryfikacji Wiedzy (PPWK)

## 1. Cel
Zapewnienie, że każda nowa informacja trafiająca do bazy wiedzy jest:
- Wiarygodna (weryfikacja źródła).
- Aktualna (data).
- Użyteczna (tagowanie biznesowe).

## 2. Proces (3 Fazy)

### Faza 1: INGEST (Pozyskanie)
- **Źródła:** Tylko autorytatywne (oficjalne dokumenty, zaufane media branżowe, dane z API, raporty firm).
- **Akcja:** Pobranie surowej treści.
  - *Uwaga:* Do wyszukiwania używamy mechanizmu web_research (patrz dokumentacja narzędzi).
- **Filtr Wstępny:** Odrzucenie treści bez daty, autora lub konkretnego źródła.

### Faza 2: VERIFY (Weryfikacja)
- **Reguła 1 (Konkretność):** Czy informacja zawiera twarde dane (liczby, nazwy, daty, linki)? Jeśli nie -> Odrzuć.
- **Reguła 2 (Sprzeczność):** Czy informacja koliduje z istniejącym wpisem w `data_vault`? 
  - Jeśli TAK: Flaguj jako `CONFLICT`. Wymaga ręcznej decyzji lub weryfikacji trzecim źródłem.
  - Jeśli NIE: Kontynuuj.
- **Reguła 3 (Relewantność):** Czy informacja dotyczy naszego biznesu (trading, AI, finanse, marketing)? 
  - Jeśli NIE: Odrzuć.
- **Poziom Pewności:**
  - **3+ źródła niezależne:** Pewność Wysoka (H).
  - **2 źródła:** Pewność Średnia (M).
  - **1 źródło:** Pewność Niska (L) -> Wymaga dodatkowego oznaczenia.

### Faza 3: STORE (Zapis)
- **Format:** JSON (dla maszyn) lub Markdown (dla ludzi).
- **Lokalizacja:** `data_vault/knowledge_base/`
- **Nazwa pliku:** `YYYY-MM-DD